import json
import pytest
from datetime import timedelta
from django.utils import timezone
from django.core import mail
from django.contrib.auth.models import User
from allauth.account.models import EmailConfirmation, EmailAddress


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
    u = User.objects.get(username='test_user')
    assert not u.profile.plus_notification_mail
    assert not u.profile.pro_notification_mail


@pytest.mark.django_db
def test_register_user_with_invalid_mail(api_client, mocker):
    send_mail = mocker.patch('django.core.mail.backends.locmem.EmailBackend')
    response = api_client.post('/api/v0/auth/registration/',
                               {'username': 'test_user',
                                'email': 'test@ccccccc.de',
                                'password1': 'test1234',
                                'password2': 'test1234'})
    assert response.status_code == 201
    assert User.objects.all().count() == 1
    send_mail.assert_called_with(fail_silently=True)


@pytest.mark.django_db
def test_register_user_interested_in_qabel_plus(api_client):
    response = api_client.post('/api/v0/auth/registration/',
                               {'username': 'test_user',
                                'email': 'test@example.com',
                                'password1': 'test1234',
                                'password2': 'test1234',
                                'plus': True})
    assert response.status_code == 201
    assert User.objects.all().count() == 1
    u = User.objects.get(username='test_user')
    assert u.profile.plus_notification_mail
    assert not u.profile.pro_notification_mail


@pytest.mark.django_db
def test_register_user_interested_in_qabel_pro(api_client):
    response = api_client.post('/api/v0/auth/registration/',
                               {'username': 'test_user',
                                'email': 'test@example.com',
                                'password1': 'test1234',
                                'password2': 'test1234',
                                'pro': True})
    assert response.status_code == 201
    assert User.objects.all().count() == 1
    u = User.objects.get(username='test_user')
    assert not u.profile.plus_notification_mail
    assert u.profile.pro_notification_mail


@pytest.mark.django_db
def test_register_user_interested_in_qabel_plus_and_pro(api_client):
    response = api_client.post('/api/v0/auth/registration/',
                               {'username': 'test_user',
                                'email': 'test@example.com',
                                'password1': 'test1234',
                                'password2': 'test1234',
                                'plus': True,
                                'pro': True})
    assert response.status_code == 201
    assert User.objects.all().count() == 1
    u = User.objects.get(username='test_user')
    assert u.profile.plus_notification_mail
    assert u.profile.pro_notification_mail


@pytest.mark.django_db
def test_register_user_without_email_should_fail(api_client):
    response = api_client.post('/api/v0/auth/registration/',
                               {'username': 'test_user',
                                'password1': 'test1234',
                                'password2': 'test1234'})
    assert response.status_code == 400
    assert User.objects.all().count() == 0


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


def test_get_own_user(api_client, user):
    other_user = User.objects.create_user('foobar')
    api_client.force_authenticate(other_user)
    response = api_client.get('/api/v0/auth/user/')
    assert {"username": "foobar", "email": "", "first_name": "", "last_name": ""}\
        == loads(response.content)


@pytest.fixture(params=['auth', 'info'])
def call_auth_resource(request, external_api_client, user, token, auth_resource_path):
    def make_request():
        if request.param == 'auth':
            payload = {'auth': 'Token {}'.format(token)}
        else:
            payload = {'user_id': user.id}
        return external_api_client.post(auth_resource_path, payload)
    return make_request


@pytest.fixture
def auth_resource_path():
    return '/api/v0/internal/user/'


def test_auth_resource(user, call_auth_resource):
    response = call_auth_resource()
    assert response.status_code == 200
    data = loads(response.content)
    assert data['user_id'] == user.id
    assert data['active'] == user.profile.is_allowed()
    assert data['block_quota'] == user.profile.block_quota
    assert data['monthly_traffic_quota'] == user.profile.monthly_traffic_quota


def test_auth_resource_with_disabled_user(call_auth_resource, user):
    user.is_active = False
    user.save()
    response = call_auth_resource()
    assert response.status_code == 200
    data = loads(response.content)
    assert data['user_id'] == user.id
    assert data['active'] is False


def test_auth_resource_invalid_auth_type(external_api_client, token, auth_resource_path):
    response = external_api_client.post(auth_resource_path, {'auth': 'Foobar {}'.format(token)})
    assert response.status_code == 400
    data = loads(response.content)
    assert data['error']


def test_auth_resource_unknown_user(external_api_client, auth_resource_path):
    response = external_api_client.post(auth_resource_path, {'auth': 'Token foobar'})
    assert response.status_code == 404
    data = loads(response.content)
    assert data['error']


def test_info_resource_unknown_user(external_api_client, user, auth_resource_path):
    response = external_api_client.post(auth_resource_path, {'user_id': user.id + 1})
    assert response.status_code == 404
    data = loads(response.content)
    assert data['error']


def test_auth_resource_no_body(external_api_client, auth_resource_path):
    response = external_api_client.post(auth_resource_path)
    assert response.status_code == 400
    data = loads(response.content)
    assert data['error']


def test_failed_auth_resource_after_7_days(external_api_client, user, token, auth_resource_path):
    user.profile.needs_confirmation_after = timezone.now() - timedelta(days=7)
    user.profile.save()
    user.profile.refresh_from_db()
    request_body = {'auth': 'Token {}'.format(token)}
    response = external_api_client.post(auth_resource_path, request_body)
    assert response.status_code == 200
    data = loads(response.content)
    assert data['active'] is False
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject.startswith('[example.com]')
    assert mail.outbox[0].body.startswith('English')

    # Check, that no new mail is send within 24 hours
    response = external_api_client.post(auth_resource_path, request_body)
    data = loads(response.content)
    assert data['active'] is False
    assert response.status_code == 200
    assert len(mail.outbox) == 1

    # Check, that a new mail is send after 24 hours
    user.profile.next_confirmation_mail = timezone.now() - timedelta(minutes=1)
    user.profile.save()
    user.profile.refresh_from_db()
    response = external_api_client.post(auth_resource_path, request_body)
    assert response.status_code == 200
    assert len(mail.outbox) == 2


def test_resource_api_key(user_client, auth_resource_path):
    response = user_client.post(auth_resource_path)
    assert response.status_code == 400, "Should require APISECRET header"


def test_logout(api_client, user):
    # We need to be logged in to logout
    api_client.post('/api/v0/auth/login/', {'username': user.username, 'password': 'password'})
    response = api_client.post('/api/v0/auth/logout/', HTTP_ACCEPT_LANGUAGE='de')
    assert response.content == b'{"success":"Erfolgreich ausgeloggt."}'


def test_login_throttle(api_client, db):
    for _ in range(4):
        response = api_client.post('/api/v0/auth/login/',
                                   {'username': 'foo', 'password': 'wrong'})
        assert response.status_code == 400
    response = api_client.post('/api/v0/auth/login/',
                               {'username': 'foo', 'password': 'wrong'})
    assert response.status_code == 429
    assert loads(response.content)['error'] == 'Too many login attempts'


@pytest.mark.django_db
def test_register_user_with_bad_password(api_client):
    response = api_client.post('/api/v0/auth/registration/',
                               {'username': 'testtest',
                                'email': 'test@example.com',
                                'password1': 'testtest',
                                'password2': 'testtest'})
    assert response.status_code == 400


@pytest.mark.django_db
def test_confirm_email(api_client, token):
    response = api_client.post('/api/v0/auth/registration/',
                               {'username': 'testtest',
                                'email': 'test@example.com',
                                'password1': 'foobar1234',
                                'password2': 'foobar1234'})
    assert response.status_code == 201
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == '[example.com] Please Confirm Your E-mail Address'
    user = User.objects.get(username='testtest')
    email = EmailAddress.objects.get(user=user.id)
    confirmation = EmailConfirmation.objects.get(email_address=email)
    assert confirmation.key
    assert confirmation.key in mail.outbox[0].body
    response = api_client.get('/account-confirm-email/{}/'.format(confirmation.key))
    assert response.status_code == 302
    email.refresh_from_db()
    assert email.verified
    assert user.profile.is_confirmed


def test_confirm_invalid_email(token, mocker, user, external_api_client, auth_resource_path):
    send_mail = mocker.patch('django.core.mail.backends.locmem.EmailBackend')
    user.profile.needs_confirmation_after = timezone.now() - timedelta(days=7)
    user.profile.save()
    user.profile.refresh_from_db()
    request_body = {'auth': 'Token {}'.format(token)}
    response = external_api_client.post(auth_resource_path, request_body)
    assert response.status_code == 200
    send_mail.assert_called_with(fail_silently=True)


def test_api_root(api_client):
    response = api_client.get('/api/v0/')
    assert response.status_code == 200


def test_no_login_throttle(api_client, user):
    for login_try in range(5):
        response = api_client.post('/api/v0/auth/login/',
                                   {'username': user.username, 'password': 'password'})
        assert response.status_code == 200, "Failed at request {}".format(login_try+0)


@pytest.mark.django_db
def test_password_reset(api_client, user):
    response = api_client.post('/api/v0/auth/password/reset/', {'email': user.email})
    assert response.status_code == 200
    assert len(mail.outbox) == 1
    mail_body = mail.outbox[0].body
    url = mail_body[mail_body.find('/accounts/reset/'):].split()[0]
    response = api_client.get(url)
    assert response.status_code == 200
    new_password = 'test123456'
    response = api_client.post(url, {'new_password1': new_password, 'new_password2': new_password})
    assert response.status_code == 302
    response = api_client.post('/api/v0/auth/login/',
                               {'username': user.username, 'password': new_password})
    assert response.status_code == 200


@pytest.mark.django_db
def test_enable_disabled_user(api_client, user, token):
    user.profile.needs_confirmation_after = timezone.now() - timedelta(days=7)
    user.profile.save()
    user.profile.refresh_from_db()
    assert user.profile.check_confirmation_and_send_mail()
    user.profile.confirm_email()

    assert not user.profile.check_confirmation_and_send_mail()
