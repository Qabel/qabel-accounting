from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User

from allauth.account.models import EmailAddress
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

import pytest

from pytest_dbfixtures.factories.postgresql import init_postgresql_database
from pytest_dbfixtures.utils import try_import

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


@pytest.fixture(scope='session', autouse=True)
def apply_database_plumbing(request, postgresql_proc):
    """Bolt pytest-dbfixtures onto Django to work around its lack of no-setup testing facilities."""
    psycopg2, config = try_import('psycopg2', request)
    settings.DATABASES['default'].update({
        'NAME': config.postgresql.db,
        'USER': config.postgresql.user,
        'HOST': postgresql_proc.host,
        'PORT': postgresql_proc.port,
    })
    init_postgresql_database(psycopg2, config.postgresql.user, postgresql_proc.host, postgresql_proc.port,
                             config.postgresql.db)
