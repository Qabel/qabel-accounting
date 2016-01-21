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
def prefix(db):
    try:
        p = Prefix.objects.get()
    except Prefix.DoesNotExist:
        u = User.objects.get(username=USERNAME)
        p = Prefix(u.id)
        p.save()
    return p

@pytest.fixture
def api_client():
    return APIClient()


