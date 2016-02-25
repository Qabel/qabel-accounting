from rest_framework import serializers
from .models import Profile, Prefix
from django.contrib.auth.models import User
from rest_auth.registration.serializers import RegisterSerializer


class UserSerializer(RegisterSerializer):
    def save(self, request):
        user = super(UserSerializer, self).save(request)
        profile = user.profile
        profile.plus_notification_mail = request.POST.get('plus', False)
        profile.pro_notification_mail = request.POST.get('pro', False)
        profile.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'email')
        read_only = ('username',)


class ProfileSerializer(serializers.ModelSerializer):
    bucket = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = ('quota', 'bucket')


