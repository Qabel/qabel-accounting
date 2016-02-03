import pytest

from django.contrib.auth.models import User
from qabel_provider.models import Prefix
from rest_framework.test import APIClient

USERNAME = 'qabel_user'


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
    return u


@pytest.fixture
def prefix(db, user):
    try:
        p = Prefix.objects.get()
    except Prefix.DoesNotExist:
        p = Prefix(user.id)
        p.save()
    return p


@pytest.fixture
def profile(user):
    return user.profile


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def api_secret(settings):
    secret = "FOOBAR"
    settings.API_SECRET = secret
    return secret


@pytest.fixture
def user_client(api_client, user, prefix):
    api_client.force_authenticate(user)
    return api_client


@pytest.fixture
def user_api_client(user, api_secret):
    client = APIClient(APISECRET=api_secret)
    client.force_authenticate(user)
    return client

