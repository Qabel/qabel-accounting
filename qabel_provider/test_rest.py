import json


def loads(foo):
    return json.loads(foo.decode('utf-8'))


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


def test_get_own_user(api_client, user):
    from django.contrib.auth.models import User
    other_user = User.objects.create_user('foobar')
    api_client.force_authenticate(other_user)
    response = api_client.get('/api/v0/user/')
    assert {"username": "foobar", "email": ""}\
        == loads(response.content)


def test_update_email(api_client, user):
    api_client.force_authenticate(user)
    response = api_client.patch('/api/v0/user', {'email': 'foo@example.com'})
    assert response.status_code == 200
    response = api_client.get('/api/v0/user/')
    assert {"username": "qabel_user", "email": "foo@example.com"}\
        == loads(response.content)

