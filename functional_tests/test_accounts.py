import pytest


@pytest.fixture
def base_url(live_server):
    return live_server.url


def test_admin_login(base_url, admin_user, browser):
    browser.visit('{0}/admin/'.format(base_url))
    browser.fill_form({'username': 'admin',
                       'password': 'password'})
    browser.find_by_value('Log in').click()
    browser.click_link_by_href('/admin/auth/user/')
    browser.click_link_by_text('admin')
    assert 'Storage quota:' in browser.html


def test_login_required(base_url, browser):
    browser.visit('{0}/accounts/profile/'.format(base_url))
    assert browser.find_by_id('id_username')


def test_login(base_url, user, browser):
    browser.visit('{0}/accounts/login/'.format(base_url))
    browser.fill_form({'username': 'qabel_user',
                       'password': 'password'})
    browser.find_by_id('id_submit').click()

    assert 'Storage quota: {0}'.format(user.profile.quota)\
           == browser.find_by_id('id_quota').first.text



