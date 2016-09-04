
import pytest

from .utils import elide, get_request_origin


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
