import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.crypto import constant_time_compare
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from . import models
from .serializers import ProfileSerializer

logger = logging.getLogger(__name__)


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


class ProfileViewSet(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = ProfileSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user.profile


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'profile': reverse('api-profile', request=request, format=format),
        'quota': reverse('api-quota', request=request, format=format),
        'prefix': reverse('api-prefix', request=request, format=format),
        'login': reverse('rest_login', request=request, format=format),
        'logout': reverse('rest_logout', request=request, format=format),
        'user': reverse('rest_user_details', request=request, format=format),
        'password_change': reverse('rest_password_change', request=request, format=format),
        'password_reset': reverse('rest_password_reset', request=request, format=format),
        'password_confirm': reverse('rest_password_reset_confirm', request=request, format=format),
    })


class PrefixList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        prefixes = request.user.prefix_set.all()
        return Response(dict(prefixes=[prefix.id for prefix in prefixes]))

    def post(self, request, format=None):
        prefix = models.Prefix.objects.create(user=request.user)
        return Response(dict(prefix=prefix.id), status=201)


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

