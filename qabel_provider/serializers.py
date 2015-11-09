from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email')
        read_only = ('username',)


class ProfileSerializer(serializers.ModelSerializer):

    bucket = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = ('quota', 'bucket')

