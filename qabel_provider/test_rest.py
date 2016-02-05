import json
import pytest
import tempfile
from django.conf import settings
from django.contrib.auth.models import User


def loads(foo):
    return json.loads(foo.decode('utf-8'))


@pytest.fixture
def user_client(api_client, user, prefix):
    api_client.force_authenticate(user)
    return api_client

@pytest.mark.django_db
def test_register_user(api_client):
    response = api_client.post('/api/v0/auth/registration/',
                               {'username': 'test_user', 'email': 'test@example.com', 'password1': 'test1234',
                                'password2': 'test1234'})
    assert response.status_code == 201
    assert User.objects.all().count() == 1


@pytest.mark.django_db
def test_forgotten_password(api_client, user):
    response2 = api_client.post('/api/v0/auth/login/', {'username': user.username, 'password': 'password'})
    assert response2.status_code == 200
    response = api_client.post('/api/v0/auth/password/change/',
                               {'new_password1': 'new_password', 'new_password2': 'new_password', 'old_password': 'password'})
    assert response.status_code == 200
    u = User.objects.get(username='qabel_user')
    assert u.password != user.password

def test_login(api_client, user):
    response = api_client.post('/api/v0/auth/login/', {'username': user.username, 'password': 'password'})
    assert "key" in loads(response.content)


def test_get_user(api_client, user):
    api_client.force_authenticate(user)
    response = api_client.get('/api/v0/auth/user/')
    assert response.status_code == 200
    assert {"first_name": "", "last_name": "",
            "username": "qabel_user", "email": "qabeluser@example.com"}\
        == loads(response.content)


def test_get_profile(api_client, user):
    api_client.force_authenticate(user)
    response = api_client.get('/api/v0/profile/')
    assert response.status_code == 200
    profile = loads(response.content)
    assert 0 == profile['quota']
    assert 'qabel' == settings.BUCKET
    assert settings.BUCKET == profile['bucket']


def test_anonymous_profile(api_client):
    response = api_client.get('/api/v0/profile/')
    assert response.status_code == 401


def test_get_own_user(api_client, user):
    from django.contrib.auth.models import User
    other_user = User.objects.create_user('foobar')
    api_client.force_authenticate(other_user)
    response = api_client.get('/api/v0/auth/user/')
    assert {"username": "foobar", "email": "", "first_name": "", "last_name": ""}\
        == loads(response.content)


def test_get_list_of_user_prefixes(api_client, user, prefix):
    api_client.force_authenticate(user)
    response = api_client.get('/api/v0/prefix/')
    assert response.status_code == 200
    prefixes = loads(response.content)
    assert str(prefix.id) == prefixes[0]


def test_create_multiple_prefixes(api_client, user, prefix):
    api_client.force_authenticate(user)
    response = api_client.post('/api/v0/prefix/')
    first_prefix = loads(response.content)
    assert response.status_code == 201
    assert first_prefix != str(prefix.id)
    response = api_client.post('/api/v0/prefix/')
    second_prefix = loads(response.content)
    assert response.status_code == 201
    assert second_prefix != str(prefix.id)
    assert first_prefix != second_prefix
    assert user.prefix_set.count() == 3
    assert {str(prefix.id), first_prefix, second_prefix} ==\
           set(loads(api_client.get('/api/v0/prefix/').content))


def test_anonymous_prefix(api_client):
    response = api_client.get('/api/v0/prefix/')
    assert response.status_code == 401


def test_auth_resource(api_client, user, prefix):
    api_client.force_authenticate(user)
    path = '/api/v0/auth/{}/test'.format(str(prefix.id))
    response = api_client.post(path)
    assert response.status_code == 204
    response = api_client.get(path)
    assert response.status_code == 204

    response = api_client.delete(path)
    assert response.status_code == 204


def test_failed_auth_resource_requests(api_client, user):
    api_client.force_authenticate(user)
    path = '/api/v0/auth/invalid/test'
    response = api_client.post(path)
    assert response.status_code == 403
    response = api_client.get(path)
    assert response.status_code == 204

    response = api_client.delete(path)
    assert response.status_code == 403
