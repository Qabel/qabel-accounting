from pathlib import Path

import pytest

from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

USERNAME = 'qabel_user'
ADMIN = 'qabel_admin'


@pytest.fixture()
def tests_output_path():
    output_path = Path(__file__).absolute().parent / 'test-output'
    output_path.mkdir(exist_ok=True)
    return output_path


@pytest.fixture
def user(db):
    try:
        u = User.objects.get(username=USERNAME)
    except User.DoesNotExist:
        u = User.objects.create_user(USERNAME, 'qabeluser@example.com',
                                     'password')
        u.is_staff = False
        u.is_superuser = False
        u.save()
        EmailAddress.objects.create(user=u, email=u.email, primary=True)
    return u


@pytest.fixture
def admin(db):
    try:
        u = User.objects.get(username=ADMIN)
    except User.DoesNotExist:
        u = User.objects.create_user(USERNAME, 'qabeladmin@example.com',
                                     'password')
        u.is_staff = True
        u.is_superuser = True
        u.save()
        EmailAddress.objects.create(user=u, email=u.email, primary=True)
    return u


@pytest.fixture
def profile(user):
    return user.profile


@pytest.fixture
def token(user):
    return Token.objects.create(user=user).key


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_secret(settings):
    secret = "FOOBAR"
    settings.API_SECRET = secret
    return secret


@pytest.fixture
def user_client(api_client, user):
    api_client.force_authenticate(user)
    return api_client


@pytest.fixture
def external_api_client(user, api_secret):
    client = APIClient(HTTP_APISECRET=api_secret)
    return client
