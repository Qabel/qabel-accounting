from collections import namedtuple

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from . import models


class UserSerializer(RegisterSerializer):

    def validate_password1(self, password):
        cleaned = super().validate_password1(password)
        username = self.initial_data['username']
        user = User(username=username)
        validate_password(cleaned, user)
        return cleaned

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


class SecondaryEmailsField(serializers.ListField):
    child = serializers.EmailField(max_length=254)


class RegisterOnBehalfSerializer(serializers.Serializer):
    RegisterOnBehalf = namedtuple('RegisterOnBehalf', 'email,secondary_emails,first_name,last_name,newsletter,language')

    email = serializers.EmailField(max_length=254)
    secondary_emails = SecondaryEmailsField(required=False, default=[])
    first_name = serializers.CharField(max_length=30, required=False, default='')
    last_name = serializers.CharField(max_length=30, required=False, default='')
    newsletter = serializers.BooleanField()
    language = serializers.CharField()

    def create(self, validated_data):
        return self.RegisterOnBehalf(**validated_data)


class PlanSubscriptionSerializer(serializers.Serializer):
    PlanSubscription = namedtuple('PlanSubscription', 'profile,plan')

    user_email = serializers.EmailField()
    plan = serializers.PrimaryKeyRelatedField(queryset=models.Plan.objects.all())

    def validate_user_email(self, email):
        if not models.User.objects.filter(email=email).count():
            raise serializers.ValidationError('No such user.')
        return email

    def create(self, validated_data):
        return self.PlanSubscription(
            profile=self._get_profile(validated_data),
            plan=validated_data['plan']
        )

    def _get_profile(self, validated_data):
        return models.Profile.objects.get(user__email=validated_data['user_email'])


class PlanIntervalSerializer(PlanSubscriptionSerializer):
    duration = serializers.DurationField()

    def create(self, validated_data):
        return models.PlanInterval(
            profile=self._get_profile(validated_data),
            plan=validated_data['plan'],
            duration=validated_data['duration'],
        )
