import pytest


@pytest.fixture
def base_url(live_server):
    return live_server.url


def test_login(base_url, user, browser):
    browser.visit('{0}/accounts/login/'.format(base_url))
    browser.fill_form({'username': 'qabel_user',
                       'password': 'password'})
    browser.find_by_id('id_submit').click()


def browse_to_users(browser, base_url):
    browser.visit('{0}/admin/'.format(base_url))
    browser.fill_form({'username': 'qabel_user',
                       'password': 'password'})
    browser.find_by_css('.submit-row > input').first.click()
    browser.find_link_by_href('/admin/auth/user/'.format(base_url)).first.click()


def test_users_detail(base_url, admin, user, browser):
    browse_to_users(browser, base_url)
    browser.find_link_by_text('qabel_user').first.click()
    assert browser.is_text_present('Plus notification mail')
    assert browser.is_text_present('Pro notification mail')
    assert not browser.find_by_id('id_profile-0-plus_notification_mail').first.checked
    assert not browser.find_by_id('id_profile-0-pro_notification_mail').first.checked
    user.profile.plus_notification_mail = True
    user.profile.pro_notification_mail = True
    user.profile.save()
    browser.reload()
    assert browser.is_text_present('Plus notification mail')
    assert browser.is_text_present('Pro notification mail')
    assert browser.find_by_id('id_profile-0-plus_notification_mail').checked
    assert browser.find_by_id('id_profile-0-pro_notification_mail').checked


def test_user_filters(base_url, admin, user, browser):
    browse_to_users(browser, base_url)
    filters = browser.find_by_id('changelist-filter').text
    assert 'plus notification' in filters
    assert 'pro notification' in filters
