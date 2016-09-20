import pytest
from django.core.exceptions import ValidationError
from rest_framework import status

from .models import Redirect, validate_redirect_from


@pytest.fixture
def simple(db):
    redirect = Redirect(redirect_from='simple', to='https://example.net/')
    redirect.save()
    return redirect


@pytest.fixture
def with_slash(db):
    redirect = Redirect(redirect_from='with/slash', to='https://example.net/')
    redirect.save()
    return redirect


def test_redirect(client, simple):
    response = client.get('/dispatch/simple/')
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == simple.to


def test_redirect_missing_final_slash(client, simple):
    response = client.get('/dispatch/simple')
    assert response.status_code == status.HTTP_301_MOVED_PERMANENTLY
    assert response.url == '/dispatch/simple/'
    response = client.get(response.url)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == simple.to


def test_redirect_not_found(client, db):
    response = client.get('/dispatch/simple/')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_redirect_no_link_given(client, db):
    response = client.get('/dispatch/')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_redirect_with_slash(client, with_slash):
    response = client.get('/dispatch/with/slash/')
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == with_slash.to


@pytest.mark.parametrize('input', (
    'foo',
    'bar/foo',
    'foo_-BAR',
    'f0009/bar',
))
def test_validate_redirect_from_not_raising(input):
    validate_redirect_from(input)


@pytest.mark.parametrize('input', (
    '',
    '/',
    '/foo',
    ' bar',
    'bar/',
    'internal space',
))
def test_validate_redirect_from_raising(input):
    with pytest.raises(ValidationError):
        validate_redirect_from(input)
