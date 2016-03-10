from django.contrib.auth.models import User
from rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.password_validation import validate_password


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
