from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .serializers import UserSerializer, ProfileSerializer
from . import aws


@login_required
def profile(request):
    return render(request, 'accounts/profile.html')


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


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


_session = aws.Session()


@api_view(['POST'])
@login_required
def token(request):
    return Response(_session.create_token(request.user, aws.TEST_POLICY, 900), status=201)


@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'token': reverse('api-token', request=request, format=format),
        'user': reverse('api-user', request=request, format=format),
        'profile': reverse('api-profile', request=request, format=format),
    })
