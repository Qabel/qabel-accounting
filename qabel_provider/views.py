from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.db.transaction import atomic
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from . import models
from .serializers import ProfileSerializer


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
        return Response([prefix.id for prefix in prefixes])

    def post(self, request, format=None):
        prefix = models.Prefix.objects.create(user=request.user)
        return Response(prefix.id, status=201)


@api_view(('GET', 'POST', 'DELETE'))
@login_required
def auth_resource(request, prefix, file_path, format=None):
    """
    Handles auth for uploads, downloads and deletes on the storage backend.

    This resource is meant for the block server which can call it to check
    if the user is authenticated. The block server should set the same
    Authorization header that itself received by the user.

    :param request: rest request
    :param prefix: string that is used as prefix on the storage
    :param file_path: path of the file in the prefix
    :param format: ignored, because the resource never responds with a body
    :return: HttpResponseBadRequest|HttpResponse(status=204)|HttpResponse(status=403)
    """
    api_key = request.META.get('APISECRET', None)
    if api_key != settings.API_SECRET:
        return HttpResponseForbidden("Invalid API key")
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        if prefix not in (str(p.id) for p in request.user.prefix_set.all()):
            return HttpResponseForbidden()
        else:
            return HttpResponse(status=204)


@api_view(('POST',))
@login_required
def quota(request):
    api_key = request.META.get('APISECRET', None)
    if api_key != settings.API_SECRET:
        return HttpResponseForbidden("Invalid API key")
    try:
        prefix_name, action, size = request.data['prefix'], request.data['action'], request.data['size']
    except KeyError:
        return HttpResponse(status=400)
    prefix = models.Prefix.get_by_name(prefix_name)
    models.handle_request(action, size, prefix, request.user)
    return HttpResponse(status=204)
