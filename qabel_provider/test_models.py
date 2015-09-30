def test_user(user):
    """ Check that we have a profile
    """
    assert user.profile.quota == 0
    assert not user.is_staff


def test_superuser(admin_user):
    assert admin_user.is_staff
    assert admin_user.profile.quota == 0
