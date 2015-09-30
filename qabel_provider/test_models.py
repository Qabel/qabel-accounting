import pytest


def test_user(user):
    """ Check that we have a profile
    """
    assert user.profile.quota == 0
    assert not user.is_staff


@pytest.fail
def test_positive_quota(user):
    """
    Allowed to fail because sqlite does not enforce integer constraints
    """
    user.profile.quota = -1
    user.profile.save()
    assert user.profile.quota == 0


def test_superuser(admin_user):
    assert admin_user.is_staff
    assert admin_user.profile.quota == 0
