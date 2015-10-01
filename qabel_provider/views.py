from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, mixins
from .serializers import UserSerializer, ProfileSerializer


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

    def get_object(self):
        return self.request.user


class ProfileViewSet(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile


