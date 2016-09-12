import json
import pytest
from datetime import timedelta
from django.utils import timezone
from django.core import mail
from django.contrib.auth.models import User
from allauth.account.models import EmailConfirmation, EmailAddress

from .models import Plan, PlanInterval, ProfilePlanLog


def loads(foo):
    return json.loads(foo.decode('utf-8'))


@pytest.fixture
def auth_resource_path():
    return '/api/v0/internal/user/'


@pytest.fixture
def plan_subscription_path():
    return '/api/v0/plan/subscription/'


@pytest.fixture
def plan_interval_path():
    return '/api/v0/plan/add-interval/'


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


def test_auth_resource(user, call_auth_resource):
    response = call_auth_resource()
    assert response.status_code == 200
    data = loads(response.content)
    assert data['user_id'] == user.id
    assert data['active'] == user.profile.is_allowed()
    plan = user.profile.plan
    assert data['block_quota'] == plan.block_quota
    assert data['monthly_traffic_quota'] == plan.monthly_traffic_quota


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

protected_apis = pytest.mark.parametrize('path', (
    auth_resource_path(),
    plan_subscription_path(),
    plan_interval_path(),
))


@protected_apis
def test_protected_api_wrong_secret(client, path):
    response = client.post(path, HTTP_APISECRET='Bullshiet! Ich kann sie nicht hören!')
    assert response.status_code == 403, 'Accepted wrong APISECRET'
    assert response.json()['error'] == 'Invalid API key'


@protected_apis
def test_protected_api(client, path):
    response = client.post(path)
    assert response.status_code == 403, "Should require APISECRET header"
    assert response.json()['error'] == 'Invalid API key'


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
        assert response.status_code == 200, "Failed at request {}".format(login_try + 0)


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


@pytest.fixture
def require_audit_log(user):
    def num_log_entries():
        return ProfilePlanLog.objects.filter(profile=user.profile).count()

    def do_assert(num_entries=None):
        nonlocal before
        after = num_log_entries()
        if num_entries is None:
            assert after > before, 'no audit log entry was created'
        else:
            assert after == before + num_entries
        before = after

    before = num_log_entries()
    return do_assert


@pytest.fixture
def require_interval_state(user):
    def do_assert(*states):
        intervals = PlanInterval.objects.filter(profile=user.profile)
        assert intervals.count() == len(states)
        for interval, required_state in zip(intervals, states):
            assert interval.state == required_state
    return do_assert


@pytest.fixture
def best_plan():
    new_great_plan = Plan(id='best_plan', name='best plan', block_quota=1, monthly_traffic_quota=2)
    new_great_plan.save()
    return new_great_plan


@pytest.fixture
def better_plan():
    new_great_plan = Plan(id='better_plan', name='even better plan', block_quota=2, monthly_traffic_quota=4)
    new_great_plan.save()
    return new_great_plan


@pytest.mark.django_db
def test_plan_subscription(external_api_client, plan_subscription_path, best_plan, user, require_audit_log):
    assert user.profile.plan.id == 'free'
    assert user.email == 'qabeluser@example.com'
    assert best_plan.id == 'best_plan'
    response = external_api_client.post(plan_subscription_path, {
        'user_email': user.email,
        'plan': best_plan.id,
    })
    assert response.status_code == 200, response.json()
    require_audit_log()
    user.profile.refresh_from_db()
    assert user.profile.plan.id == best_plan.id


@pytest.mark.django_db
def test_plan_subscription_plan_missing(external_api_client, plan_subscription_path, user):
    assert user.profile.plan.id == 'free'
    assert user.email == 'qabeluser@example.com'
    response = external_api_client.post(plan_subscription_path, {
        'user_email': user.email,
    })
    assert response.status_code == 400, response.json()
    assert 'plan' in response.json()
    user.profile.refresh_from_db()
    assert user.profile.plan.id == 'free'


@pytest.mark.django_db
def test_plan_subscription_user_not_found(external_api_client, plan_subscription_path):
    response = external_api_client.post(plan_subscription_path, {
        'user_email': 'noqabeluser@example.com',
        'plan': 'free',
    })
    assert response.status_code == 400, response.json()
    assert 'user_email' in response.json()


@pytest.mark.django_db
def test_plan_subscription_plan_not_found(external_api_client, plan_subscription_path, user):
    assert user.profile.plan.id == 'free'
    assert user.email == 'qabeluser@example.com'
    response = external_api_client.post(plan_subscription_path, {
        'user_email': user.email,
        'plan': 'no-such-plan',
    })
    json = response.json()
    assert response.status_code == 400, json
    assert 'plan' in json
    assert len(json['plan']) == 1
    assert 'does not exist' in json['plan'][0]
    user.profile.refresh_from_db()
    assert user.profile.plan.id == 'free'


@pytest.mark.django_db
def test_plan_interval(external_api_client, plan_interval_path, best_plan, user, require_audit_log):
    response = external_api_client.post(plan_interval_path, {
        'user_email': user.email,
        'plan': best_plan.id,
        'duration': '30 00'  # [DD] [HH:[MM:]]ss[.uuuuuu], ie. 30 days, 0 seconds
    })
    assert response.status_code == 200, response.json()
    require_audit_log()

    profile = user.profile
    assert profile.plan.id == best_plan.id
    assert profile.subscribed_plan.id == 'free'  # unchanged
    # Merely taking a peek doesn't make the plan interval used
    require_interval_state('pristine')
    require_audit_log(num_entries=0)

    # Have to signal active use of the plan
    profile.use_plan()
    require_interval_state('in_use')
    require_audit_log(num_entries=1)


@pytest.mark.django_db
def test_plan_interval_multiple(external_api_client, user,
                                plan_interval_path, best_plan, better_plan,
                                require_audit_log, require_interval_state):
    response = external_api_client.post(plan_interval_path, {
        'user_email': user.email,
        'plan': best_plan.id,
        'duration': '1'
    })
    assert response.status_code == 200, response.json()
    require_audit_log()

    response = external_api_client.post(plan_interval_path, {
        'user_email': user.email,
        'plan': better_plan.id,
        'duration': '1'
    })
    assert response.status_code == 200, response.json()
    require_audit_log()

    profile = user.profile
    require_interval_state('pristine', 'pristine')
    assert profile.plan.id == better_plan.id  # most recently added interval wins
    require_interval_state('pristine', 'pristine')
    require_audit_log(num_entries=0)

    profile.use_plan()
    require_interval_state('in_use', 'pristine')
    require_audit_log(num_entries=1)
    assert profile.plan.id == better_plan.id


@pytest.mark.django_db
def test_plan_interval_expiry(external_api_client, plan_interval_path, best_plan, user, mocker, require_audit_log, require_interval_state):
    response = external_api_client.post(plan_interval_path, {
        'user_email': user.email,
        'plan': best_plan.id,
        'duration': '1'
    })
    assert response.status_code == 200, response.json()
    require_audit_log()

    profile = user.profile

    require_interval_state('pristine')
    assert profile.plan.id == best_plan.id
    require_audit_log(num_entries=0)
    require_interval_state('pristine')

    profile.use_plan()
    require_audit_log(num_entries=1)
    require_interval_state('in_use')

    some_bit_in_the_future = timezone.now() + timedelta(minutes=1)
    timezone.now = mocker.Mock(spec=timezone.now)
    timezone.now.return_value = some_bit_in_the_future

    assert profile.plan.id == 'free'
    require_audit_log(num_entries=1)
    require_interval_state('expired')
