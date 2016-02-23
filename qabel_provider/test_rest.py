import json
import pytest
from django.conf import settings
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.core import mail


def loads(foo):
    return json.loads(foo.decode('utf-8'))


@pytest.mark.django_db
def test_register_user(api_client):
    response = api_client.post('/api/v0/auth/registration/',
                               {'username': 'test_user',
                                'email': 'test@example.com',
                                'password1': 'test1234',
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
    response = api_client.post('/api/v0/auth/login/',
                               {'username': user.username, 'password': 'password'})
    assert "key" in loads(response.content)


def test_get_user(user_client):
    response = user_client.get('/api/v0/auth/user/')
    assert response.status_code == 200
    assert {"first_name": "", "last_name": "",
            "username": "qabel_user", "email": "qabeluser@example.com"}\
        == loads(response.content)


def test_get_profile(user_client):
    response = user_client.get('/api/v0/profile/')
    assert response.status_code == 200
    profile = loads(response.content)
    assert 0 == profile['quota']
    assert 0 == profile['used_storage']
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


def test_get_list_of_user_prefixes(user_client, prefix):
    response = user_client.get('/api/v0/prefix/')
    assert response.status_code == 200
    prefixes = loads(response.content)['prefixes']
    assert str(prefix.id) == prefixes[0]


def test_create_multiple_prefixes(user_client, user, prefix):
    response = user_client.post('/api/v0/prefix/')
    first_prefix = loads(response.content)['prefix']
    assert response.status_code == 201
    assert first_prefix != str(prefix.id)
    response = user_client.post('/api/v0/prefix/')
    second_prefix = loads(response.content)['prefix']
    assert response.status_code == 201
    assert second_prefix != str(prefix.id)
    assert first_prefix != second_prefix
    assert user.prefix_set.count() == 3
    assert {str(prefix.id), first_prefix, second_prefix} ==\
           set(loads(user_client.get('/api/v0/prefix/').content)['prefixes'])


def test_anonymous_prefix(api_client):
    response = api_client.get('/api/v0/prefix/')
    assert response.status_code == 401


def test_auth_resource(user_api_client, prefix, api_secret):
    path = '/api/v0/auth/{}/test'.format(str(prefix.id))
    response = user_api_client.post(path)
    assert response.status_code == 204
    response = user_api_client.get(path)
    assert response.status_code == 204

    response = user_api_client.delete(path)
    assert response.status_code == 204


def test_failed_auth_resource_requests(user_api_client, user, api_secret):
    path = '/api/v0/auth/invalid/test'
    response = user_api_client.post(path)
    assert response.status_code == 403
    response = user_api_client.get(path)
    assert response.status_code == 204
    response = user_api_client.delete(path)
    assert response.status_code == 403


def test_failed_auth_resource_after_7_days(user_api_client, prefix, api_secret, user):
    user.profile.needs_confirmation_after = timezone.now() - timedelta(days=7)
    user.profile.save()
    user.profile.refresh_from_db()
    path = '/api/v0/auth/{}/test'.format(str(prefix.id))
    response = user_api_client.post(path)
    assert response.status_code == 401
    assert response.content == b'E-Mail address is not confirmed'
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == 'Please confirm your e-mail address'
    assert mail.outbox[0].body == 'Please confirm your e-mail address with this link:'

    # Check, that no new mail is send within 24 hours
    response = user_api_client.post(path)
    assert response.status_code == 401
    assert len(mail.outbox) == 1

    # Check, that a new mail is send after 24 hours
    user.profile.next_confirmation_mail = timezone.now() - timedelta(minutes=1)
    user.profile.save()
    user.profile.refresh_from_db()
    response = user_api_client.post(path)
    assert response.status_code == 401
    assert len(mail.outbox) == 2


def test_auth_resource_api_key(user_client, prefix, api_secret):
    path = '/api/v0/auth/{}/test'.format(str(prefix.id))
    response = user_client.post(path)
    assert response.status_code == 400, "Should require APISECRET header"


def test_quota_tracking_post(user_client, prefix, profile, api_secret):
    path = '/api/v0/quota/'
    size = 2492

    response = user_client.post(path, {
        "prefix": str(prefix),
        "file_path": "foo/bar/baz.txt",
        "action": "store",
        "size": size},
        HTTP_APISECRET=api_secret)
    assert response.status_code == 204
    prefix.refresh_from_db()
    assert prefix.size == size
    user = prefix.user
    profile = user.profile
    assert profile.used_storage == size
    profile.refresh_from_db()


def test_invalid_api_key(user_client, prefix, profile, api_secret):
    path = '/api/v0/quota/'

    response = user_client.post(path, {
        "prefix": str(prefix),
        "file_path": "foo/bar/baz.txt",
        "action": "store",
        "size": 1})
    assert response.status_code == 400

