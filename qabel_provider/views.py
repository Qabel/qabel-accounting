import boto3
import tempfile
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .serializers import ProfileSerializer
from . import models
from rest_framework.views import APIView
from botocore.exceptions import ClientError
from django.http import Http404, HttpResponse, FileResponse, HttpResponseForbidden, \
    HttpResponseBadRequest
from django.conf import settings


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

client = boto3.client('s3')
transfer = boto3.s3.transfer.S3Transfer(client)
s3 = boto3.resource('s3')


@api_view(('GET', 'POST', 'DELETE'))
@login_required()
def file_resource(request, prefix, file_path, format=None):
    """
    Handles uploads, downloads and deletes on the storage backend.

    All methods require authentication and upload/delete require that the
     user has access to the specified prefix.

     Delete requests for file that do not exists are always successful
    :param request: rest request
    :param prefix: string that is used as prefix on the storage
    :param file_path: path of the file in the prefix
    :param format: ignored, because the resource never responds with a body that is not a file
    :return: FileResponse|HttpResponseBadRequest|HttpResponse(status=204)
    """
    file_key = '{}/{}'.format(prefix, file_path)
    if request.method == 'GET':
        try:
            with tempfile.NamedTemporaryFile('wb') as temp:
                transfer.download_file(settings.BUCKET, file_key, temp.name)
                temp.flush()
                response = FileResponse(open(temp.name, 'rb'),
                                        content_type='application/octet-stream')
                return response
        except ClientError:
            # boto3 error, which means that he download failed
            raise Http404("File not found")
    else:
        if prefix not in (str(p.id) for p in request.user.prefix_set.all()):
            return HttpResponseForbidden()
        if request.method == 'POST':
            file = request.FILES.get('file', None)
            if file is None:
                return HttpResponseBadRequest()
            transfer.upload_file(file.temporary_file_path(), settings.BUCKET, file_key)
        elif request.method == 'DELETE':
            s3.Object(settings.BUCKET, file_key).delete()
        return HttpResponse(status=204)
