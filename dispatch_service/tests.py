import pytest
from rest_framework import status

from .models import Redirect


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


def test_redirect_not_found(client, db):
    response = client.get('/dispatch/simple/')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_redirect_with_slash(client, with_slash):
    response = client.get('/dispatch/with/slash/')
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == with_slash.to
