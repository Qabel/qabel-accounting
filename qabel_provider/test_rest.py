import json
import pytest


def loads(foo):
    return json.loads(foo.decode('utf-8'))


@pytest.fixture
def user_client(api_client, user):
    api_client.force_authenticate(user)
    return api_client


def test_login(api_client, user):
    response = api_client.post('/api-auth/login', {'username': user.username, 'password': 'password'})
    # redirect to profile page which we can ignore.
    assert response.status_code == 301


def test_get_user(api_client, user):
    api_client.force_authenticate(user)
    response = api_client.get('/api/v0/user/')
    assert response.status_code == 200
    assert {"username": "qabel_user", "email": "qabeluser@example.com"}\
        == loads(response.content)


def test_get_profile(api_client, user):
    api_client.force_authenticate(user)
    response = api_client.get('/api/v0/profile/')
    assert response.status_code == 200
    assert {"quota": 0} == loads(response.content)


def test_anonymous_profile(api_client):
    response = api_client.get('/api/v0/profile/')
    assert response.status_code == 403


def test_get_own_user(api_client, user):
    from django.contrib.auth.models import User
    other_user = User.objects.create_user('foobar')
    api_client.force_authenticate(other_user)
    response = api_client.get('/api/v0/user/')
    assert {"username": "foobar", "email": ""}\
        == loads(response.content)


def test_update_email(user_client):
    response = user_client.patch('/api/v0/user/', {'email': 'foo@example.com'})
    assert response.status_code == 200
    response = user_client.get('/api/v0/user/')
    assert {"username": "qabel_user", "email": "foo@example.com"}\
        == loads(response.content)


def test_verify_email(user_client):
    response = user_client.patch('/api/v0/user/', {'email': 'invalid'})
    assert response.status_code == 400


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

