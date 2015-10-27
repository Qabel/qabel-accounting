import json
import pytest
from django.conf import settings


def loads(foo):
    return json.loads(foo.decode('utf-8'))


@pytest.fixture
def user_client(api_client, user):
    api_client.force_authenticate(user)
    return api_client


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
    assert user.profile.prefix == profile['prefix']
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


def test_get_federation_token(user_client):
    response = user_client.post('/api/v0/token/')
    assert response.status_code == 201
    j = response.data
    c = j['Credentials']
    assert c['AccessKeyId']
    assert c['SecretAccessKey']
    assert c['SessionToken']
    assert c['Expiration']
    u = j['FederatedUser']
    assert u['FederatedUserId']
    assert u['Arn']
    assert int(j['PackedPolicySize'])

