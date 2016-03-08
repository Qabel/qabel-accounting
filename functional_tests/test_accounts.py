import pytest


@pytest.fixture
def base_url(live_server):
    return live_server.url


def test_login(base_url, user, browser):
    browser.visit('{0}/accounts/login/'.format(base_url))
    browser.fill_form({'username': 'qabel_user',
                       'password': 'password'})
    browser.find_by_id('id_submit').click()
