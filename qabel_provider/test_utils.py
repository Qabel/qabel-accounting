
from django.contrib.auth.models import User

import pytest

from .utils import elide, get_request_origin, gen_username


@pytest.mark.parametrize('text, length, output', (
    ('1234', None, '1234'),
    ('12345', 4, '1...'),
))
def test_elide(text, length, output):
    assert elide(text, length) == output


def request(meta):
    class Request:
        META = meta
    return Request()


@pytest.mark.parametrize('meta, origin', (
    ({'REMOTE_USER': 'Manfred'}, "user 'Manfred'"),
    ({'REMOTE_USER': 'Robert\'); DROP QUOTE'}, 'user "Robert\'); DROP QUOTE"'),
    (
        {
            'REMOTE_USER': 'qbl-billing01',
            'REMOTE_ADDR': '10.1.2.3',
            'REMOTE_HOST': 'qbl-billing01.cheapercloud.net',
        },
        "user 'qbl-billing01', address '10.1.2.3', host 'qbl-billing01.cheapercloud.net'"),
))
def test_get_request_origin(meta, origin):
    assert get_request_origin(request(meta)) == origin


def test_gen_username(db):
    assert gen_username('user@xyz') == 'user'


def test_gen_username_existing(db):
    User.objects.create_user('user')
    assert gen_username('user@xyz') == 'user1'


def test_gen_username_many_existing(db):
    User.objects.create_user('user')
    User.objects.create_user('user1')
    assert gen_username('user@xyz') == 'user2'


def test_gen_username_too_long(db):
    too_long = 'abcdefghijklmnopqrstuvwxyz12345@xyz'
    assert len(too_long) > 30
    assert gen_username(too_long) != too_long
