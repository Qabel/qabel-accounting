import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.crypto import constant_time_compare
from rest_auth.views import LoginView
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.authtoken.models import Token
from axes import decorators as axes_dec

logger = logging.getLogger(__name__)


@login_required
@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'quota': reverse('api-quota', request=request, format=format),
        'prefix': reverse('api-prefix', request=request, format=format),
        'login': reverse('rest_login', request=request, format=format),
        'logout': reverse('rest_logout', request=request, format=format),
        'user': reverse('rest_user_details', request=request, format=format),
        'password_change': reverse('rest_password_change', request=request, format=format),
        'password_reset': reverse('rest_password_reset', request=request, format=format),
        'password_confirm': reverse('rest_password_reset_confirm', request=request, format=format),
    })


def check_api_key(request):
    api_key = request.META.get('HTTP_APISECRET', None)
    return constant_time_compare(
            api_key, settings.API_SECRET)


@api_view(('POST',))
def auth_resource(request, format=None):
    """
    Handles auth for uploads, downloads and deletes on the storage backend.

    This resource is meant for the block server which can call it to check
    if the user is authenticated. The block server should set the same
    Authorization header that itself received by the user.

    :param request: rest request
    :param format: ignored, because the resource never responds with a body
    :return: HttpResponseBadRequest|HttpResponse(status=204)|HttpResponse(status=403)
    """
    if not check_api_key(request):
        logger.warning('Called with invalid API key')
        return HttpResponse("Invalid API key", status=400)

    try:
        user_auth = request.data['auth']
    except KeyError:
        return Response(status=400, data={'error': 'No auth given'})
    try:
        auth_type, token = user_auth.split()
        if auth_type != 'Token':
            raise ValueError()
    except ValueError:
        return Response(status=400, data={'error': 'Invalid auth type'})

    try:
        token_object = Token.objects.get(key=token)
    except Token.DoesNotExist:
        return Response(status=404, data={'error': 'Invalid token'})
    user = token_object.user

    logger.debug('Auth resource called: user={}'.format(user))
    is_disabled = user.profile.check_confirmation_and_send_mail()
    return Response({'user_id': user.id, 'active': (not is_disabled)})


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

        if self.watch_login(request, False):
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

