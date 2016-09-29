import functools
import hashlib
import hmac
import os
import logging
from smtplib import SMTPException

from allauth.account.models import EmailAddress
from axes import decorators as axes_dec
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django import forms
from django.shortcuts import redirect
from django.template import loader
from django.template.response import TemplateResponse as render
from django.utils.translation import ugettext_lazy as _
from rest_auth.registration.views import RegisterView
from rest_auth.views import LoginView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse

from log_request_id import local as request_local

from .block import get_block_quota_of_user
from .serializers import UserSerializer, PlanSubscriptionSerializer, PlanIntervalSerializer, RegisterOnBehalfSerializer
from .models import ProfilePlanLog
from .utils import get_request_origin, gen_username

logger = logging.getLogger(__name__)


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'register': reverse('rest_register', request=request, format=format),
        'verify-email': reverse('rest_verify_email', request=request, format=format),
        'auth': reverse('api-auth', request=request, format=format),
        'login': reverse('rest_login', request=request, format=format),
        'logout': reverse('rest_logout', request=request, format=format),
        'user': reverse('rest_user_details', request=request, format=format),
        'password_change': reverse('rest_password_change', request=request, format=format),
        'password_reset': reverse('rest_password_reset', request=request, format=format),
        'password_confirm': reverse('rest_password_reset_confirm', request=request, format=format),
    })


@functools.lru_cache()
def hashed_api_secret():
    return hashlib.sha512(settings.API_SECRET.encode()).digest()


def check_api_key(request):
    api_key = request.META.get('HTTP_APISECRET', '')
    # Avoid leaking length of the APISECRET via comparison timing.
    hashed_key = hashlib.sha512(api_key.encode()).digest()
    return hmac.compare_digest(hashed_key, hashed_api_secret())


def api_key_error():
    logger.warning('Called with invalid API key')
    return Response(status=403, data={'error': 'Invalid API key'})


def require_api_key(view):
    @functools.wraps(view)
    def view_wrapper(request, format=None):
        if not check_api_key(request):
            return api_key_error()
        # Request authorized by API key, so imbue our logs with X-Request-ID
        request_id = request.META.get('HTTP_X_REQUEST_ID')
        if request_id:
            request_local.request_id = request_id
            request.id = request_id
        return view(request, format)
    return view_wrapper


@api_view(('POST',))
@require_api_key
def auth_resource(request, format=None):
    """
    Handles auth for uploads, downloads and deletes on the storage backend.

    This returns user data by either passing an authentication token
    presented by the user (*auth*) or by passing an user ID (*user_id*).

    The first case authenticates the user to the client of this API, the second
    obviously doesn't.

    This resource is meant for the block server which can call it to check
    if the user is authenticated. The block server should set the same
    Authorization header that itself received by the user.

    :return: HttpResponseBadRequest|HttpResponse(status=204)|HttpResponse(status=403)|HttpResponse(status=404)
    """
    if 'auth' in request.data and 'user_id' in request.data:
        return Response(status=400, data={'error': 'Pass *either* an auth token *or* an user ID'})
    elif 'auth' in request.data:
        user_auth = request.data['auth']
        try:
            auth_type, token = user_auth.split()
            if auth_type != 'Token':
                raise ValueError()
        except ValueError:
            return Response(status=400, data={'error': 'Invalid auth type'})
        try:
            user = Token.objects.get(key=token).user
        except Token.DoesNotExist:
            return Response(status=404, data={'error': 'Invalid token'})
    elif 'user_id' in request.data:
        try:
            user_id = int(request.data['user_id'])
        except (KeyError, ValueError):
            return Response(status=400, data={'error': 'Malformed user ID'})
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=404, data={'error': 'Invalid user ID'})
    else:
        return Response(status=400, data={'error': 'No user identification supplied'})

    logger.debug('Auth resource called: user={}'.format(user))
    is_disabled = user.profile.check_confirmation_and_send_mail()
    profile = user.profile
    profile.use_plan()
    return Response({
        'user_id': user.id,
        'active': (not is_disabled),
        'block_quota': profile.plan.block_quota,
        'monthly_traffic_quota': profile.plan.monthly_traffic_quota,
    })


class PasswordSetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        cc_emails = context.pop('cc_emails')
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email], cc=cc_emails)
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()

    def save(self, cc_emails, **kwargs):
        # Judica me, Deus, et discerne causam meam de gente non sancta: ab homine iniquo et doloso erue me.
        extra_email_context = kwargs.setdefault('extra_email_context', {})
        extra_email_context['cc_emails'] = cc_emails
        super().save(**kwargs)


@api_view(('POST',))
@require_api_key
def register_on_behalf(request, format=None):
    serializer = RegisterOnBehalfSerializer(data=request.data)
    serializer.is_valid(True)
    userdata = serializer.save()

    try:
        with transaction.atomic():
            if User.objects.filter(email=userdata.email).count():
                return Response({'status': 'Account exists'})

            username = gen_username(userdata.email)

            # We set a very long, random password because PasswordResetForm requires a usable password
            # (to avoid having disabled-by-staff users re-enable their accounts via a passwort reset).
            password = os.urandom(64).hex()
            user = User.objects.create_user(username,
                                            email=userdata.email,
                                            password=password,
                                            first_name=userdata.first_name,
                                            last_name=userdata.last_name)
            EmailAddress.objects.create(user=user, email=userdata.email,
                                        primary=True, verified=True)
            for email in userdata.secondary_emails:
                EmailAddress.objects.create(user=user, email=email,
                                            primary=False, verified=True)
            user.profile.created_on_behalf = True
            user.profile.save()

            password_form = PasswordSetForm(data={'email': userdata.email})
            if not password_form.is_valid():
                # Should not be possible to hit, unless drf3 and django use different email validators w/ different accepting sets
                logger.error('register_on_behalf failed, password reset form with validated email is invalid?! '
                             'Errors are: %r', password_form.errors)
                return Response({'status': 'Registration failed.'}, status=500)

            password_form.save(
                cc_emails=userdata.secondary_emails,
                request=request,
                use_https=request.is_secure(),
                from_email=settings.DEFAULT_FROM_EMAIL,
                subject_template_name='registration/account_created_subject.txt',
                email_template_name='registration/account_created_email.txt',
                html_email_template_name='registration/account_created_email.html'
            )
    except SMTPException as smtp_exception:
        # zodb has a much, much nicer design here. You can just call doom() inside a transaction, trying to commit it
        # will fail (with an exception). Leaving the scope does not. Intuitive, correct, avoids huge exception handlers.
        logger.exception('register_on_behalf failed while sending mail')
        return Response({'status': 'Registration failed. SMTP error: %s' % smtp_exception}, status=400)

    return Response({'status': 'Account created'})


@api_view(('POST',))
@require_api_key
def plan_subscription(request, format=None):
    """
    Set subscription for an user account.

    Payload layout::

        {
            'user_email': STR,
            'plan': STR (id-of-plan),
        }

    API authentication required.
    """
    serializer = PlanSubscriptionSerializer(data=request.data)
    serializer.is_valid(True)
    profile, plan = serializer.save()

    audit_log = ProfilePlanLog(profile=profile,
                               action='set-plan', plan=plan,
                               origin=get_request_origin(request))

    with transaction.atomic():
        profile.subscribed_plan = plan
        profile.save()
        audit_log.save()

    return Response()


@api_view(('POST',))
@require_api_key
def plan_add_interval(request, format=None):
    """
    Add plan interval to an user account.

    Payload layout::

        {
            'user_email': STR,
            'plan': STR (id-of-plan),
            'duration': STR ([DD] [HH:[MM:]]ss[.uuuuuu]),
        }

    For details on *duration*, see http://www.django-rest-framework.org/api-guide/fields/#durationfield
    """
    serializer = PlanIntervalSerializer(data=request.data)
    serializer.is_valid(True)
    plan_interval = serializer.save()

    audit_log = ProfilePlanLog(profile=plan_interval.profile,
                               action='add-interval', interval=plan_interval, plan=plan_interval.plan,
                               origin=get_request_origin(request))

    with transaction.atomic():
        plan_interval.save()
        audit_log.save()

    return Response()


class ThrottledLoginView(LoginView):

    @staticmethod
    def lockout_response():
        return Response(status=429, data={'error': 'Too many login attempts'})

    # noinspection PyAttributeOutsideInit
    def post(self, request, *args, **kwargs):
        if axes_dec.is_already_locked(request):
            return self.lockout_response()

        self.serializer = self.get_serializer(data=self.request.data)
        try:
            self.serializer.is_valid(raise_exception=True)
        except ValidationError:
            if self.watch_login(request, False):
                raise
            else:
                return self.lockout_response()

        if self.watch_login(request, True):
            self.login()
            return self.get_response()
        else:
            return self.lockout_response()

    @staticmethod
    def watch_login(request, successful):
        axes_dec.AccessLog.objects.create(
            user_agent=request.META.get('HTTP_USER_AGENT', '<unknown>')[:255],
            ip_address=axes_dec.get_ip(request),
            username=request.data['username'],
            http_accept=request.META.get('HTTP_ACCEPT', '<unknown>'),
            path_info=request.META.get('PATH_INFO', '<unknown>'),
            trusted=successful
        )
        return axes_dec.check_request(request, not successful)


class PasswordPolicyRegisterView(RegisterView):
    serializer_class = UserSerializer


def get_used_quota_of_user(user):
    cache_key = 'user-quota-%d' % user.id
    quota_used = cache.get(cache_key)
    if quota_used is not None:
        return quota_used
    try:
        _, quota_used = get_block_quota_of_user(user)
    except Exception:
        logger.exception('Unable to retrieve block quota.')
        return 0
    else:
        cache.set(cache_key, quota_used, 60)
        return quota_used


@login_required
def user_profile(request):
    user = request.user
    profile = user.profile

    quota_used = get_used_quota_of_user(user)
    user_greeting = '{} {}'.format(user.first_name, user.last_name).strip() or user.username

    return render(request, 'accounts/profile.html', {
        'user_greeting': user_greeting,
        'profile': profile,
        'block_used': quota_used,
        'block_quota': profile.plan.block_quota,
        'block_percentage': int((quota_used / profile.plan.block_quota) * 100),
    })


class ProfileForm(forms.ModelForm):
    primary_email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        profile = kwargs['instance'].profile
        if profile.primary_email:
            kwargs.setdefault('initial', {})['primary_email'] = profile.primary_email.email
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        new_mail = self.cleaned_data['primary_email']
        primary_mail = self.instance.profile.primary_email
        if not primary_mail:
            EmailAddress.objects.create(email=new_mail, user=self.instance, primary=True)
        else:
            primary_mail.verified = False
            primary_mail.email = new_mail
            primary_mail.save()
        self.instance.profile.check_confirmation_and_send_mail()
        return super().save(commit)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',)


@login_required
def change_user_profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.POST and form.is_valid():
        form.save()
        return redirect(user_profile)
    return render(request, 'accounts/change_profile.html', {
        'form': form,
        'title': _('Change profile'),
    })

event_describers = {
    'start-interval': _('Started using prepaid plan {.plan}').format,
    'expired-interval': _('Prepaid plan {.plan} expired').format,
    'add-interval': _('Prepaid plan {.plan} of duration {.interval.duration} added').format,
    'set-plan': _('Subscribed to {.plan}').format,
}


@login_required
def user_history(request):
    user = request.user
    profile = user.profile

    events = []
    for event in ProfilePlanLog.objects.filter(profile=profile):
        events.append(event_describers[event.action](event))

    return render(request, 'accounts/history.html', {
        'profile': profile,
        'events': events,
    })


def user_login(request, **kwargs):
    if request.user.is_authenticated():
        return redirect(user_profile)  # Could introspect "next" etc here
    return login(request, **kwargs)


def user_mail_confirmed(request):
    return render(request, 'accounts/confirmed.html')
