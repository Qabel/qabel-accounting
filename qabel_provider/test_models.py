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

