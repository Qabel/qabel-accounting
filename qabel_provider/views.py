from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .serializers import UserSerializer, ProfileSerializer, PrefixSerializer
from . import aws
from rest_framework.views import APIView
from django.contrib.auth.models import User

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


_session = aws.Session()


@api_view(['POST'])
@login_required
def token(request):
    return Response(_session.create_token(request.user,
                                          aws.Policy(request.user).json,
                                          900),
                    status=201)

@api_view(('GET',))
def api_root(request, format=None):
    return Response({
        'token': reverse('api-token', request=request, format=format),
        'profile': reverse('api-profile', request=request, format=format),
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
        serializer = PrefixSerializer(prefixes, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        user = User.objects.get(username=request.data['user'])
        data = {'user': user.id}
        serializer = PrefixSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
