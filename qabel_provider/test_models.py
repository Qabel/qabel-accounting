from datetime import timedelta
from django.utils import timezone
import pytest
from qabel_provider import models

SIZE = 2096


def test_user(user):
    """ Check that we have a profile
    """
    assert user.profile.quota == 0
    assert not user.is_staff


def test_superuser(admin_user):
    assert admin_user.is_staff
    assert admin_user.profile.quota == 0


def test_quote_related_defaults(profile, prefix):
    assert profile.used_storage == 0
    assert profile.prefix_downloads == 0
    assert prefix.size == 0
    assert prefix.downloads == 0


def test_quota_tracking_store(profile, prefix):
    assert profile.used_storage == 0
    assert prefix.size == 0
    models.handle_request('store', SIZE, prefix, prefix.user)
    profile.refresh_from_db()
    prefix.refresh_from_db()
    assert profile.prefix_downloads == 0
    assert profile.used_storage == SIZE
    assert prefix.downloads == 0
    assert prefix.size == SIZE


def test_quota_tracking_delete(profile, prefix):
    models.handle_store(SIZE, prefix, prefix.user)
    models.handle_request(
            'store', -SIZE, prefix, prefix.user)
    profile.refresh_from_db()
    prefix.refresh_from_db()
    assert profile.used_storage == 0
    assert prefix.size == 0


def test_quota_tracking_get(profile, prefix):
    assert profile.downloads == 0

    models.handle_request('get', SIZE, prefix, prefix.user)
    profile.refresh_from_db()
    prefix.refresh_from_db()

    # no side effects
    assert profile.used_storage == 0
    assert prefix.size == 0

    assert profile.downloads == SIZE
    assert prefix.downloads == SIZE
    assert profile.prefix_downloads == SIZE


def test_quota_invalid_method(prefix):
    with pytest.raises(TypeError):
        models.handle_request('invalid', 0, prefix, prefix.user)


def test_prefix_by_str(prefix):
    assert prefix.id == models.Prefix.get_by_name(str(prefix)).id


def test_profile_is_not_confirmed_but_allowed(profile):
    assert profile.is_allowed()


def test_profile_is_confirmed_and_allowed(profile):
    profile.is_confirmed = True
    profile.save()
    profile.refresh_from_db()
    assert profile.is_allowed()


def test_profile_is_disabled(profile):
    profile.is_disabled = True
    profile.save()
    profile.refresh_from_db()
    assert not profile.is_allowed()

    profile.is_confirmed = True
    profile.save()
    profile.refresh_from_db()
    assert not profile.is_allowed()


def test_profile_is_not_confirmed_and_confirmation_date_exceeded(profile):
    profile.needs_confirmation_after = timezone.now()
    profile.save()
    profile.refresh_from_db()
    assert not profile.is_allowed()


def test_email_sent_1_day_ago(profile):
    profile.email_confirmation_date = timezone.now() - timedelta(days=1)
    profile.save()
    profile.refresh_from_db()
    assert not profile.was_email_sent_last_24_hours()
