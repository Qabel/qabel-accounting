"""qabel_id URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import urls as auth_urls
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as _context
from qabel_provider import views
from rest_auth.views import (
    LogoutView, UserDetailsView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)
from rest_auth.registration.views import VerifyEmailView
from allauth.account.views import ConfirmEmailView, EmailVerificationSentView
import nested_admin.urls

from qabel_web_theme import urls as theme_urls
from dispatch_service.views import dispatch

rest_auth_register_urls = [
    url(r'^$', views.PasswordPolicyRegisterView.as_view(), name='rest_register'),
    url(r'^verify-email/$', VerifyEmailView.as_view(), name='rest_verify_email'),
]

rest_auth_urls = [
    url(r'^password/reset/$', PasswordResetView.as_view(),
        name='rest_password_reset'),
    url(r'^password/reset/confirm/$', PasswordResetConfirmView.as_view(),
        name='rest_password_reset_confirm'),
    url(r'^login/$', views.ThrottledLoginView.as_view(), name='rest_login'),
    url(r'^logout/$', LogoutView.as_view(), name='rest_logout'),
    url(r'^user/$', UserDetailsView.as_view(), name='rest_user_details'),
    url(r'^password/change/$', PasswordChangeView.as_view(),
        name='rest_password_change'),
]

rest_urls = [
    url(r'^$', views.api_root, name='api-root'),
    url(r'^auth/', include(rest_auth_urls)),
    url(r'^auth/registration/', include('rest_auth.registration.urls')),
    url(r'^internal/user/$', views.auth_resource, name='api-auth'),
    url(r'^internal/user/register/$', views.register_on_behalf),

    url(r'^plan/subscription/$', views.plan_subscription),
    url(r'^plan/add-interval/$', views.plan_add_interval),
]

profile_urls = [
    url(r'^$', views.user_profile, name='user-profile'),
    url(r'^account/history$', views.user_history),
    url(r'^change/profile$', views.change_user_profile, name='change-user-profile'),
]

if not settings.FACET_USER_PROFILE:
    # knock knock
    profile_urls.clear()


dispatch_urls = [
    url(r'(?P<redirect_from>.*)/$', dispatch, name='dispatch'),
]


def redirect_to_login(request):
    return redirect(reverse(views.user_login) + '?' + request.GET.urlencode())

urlpatterns = [
    url(r'^dispatch/', include(dispatch_urls)),
    url(r'^admin/login/$', redirect_to_login),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^nested_admin/', include(nested_admin.urls)),
    url(r'^accounts/login/', views.user_login, name='login'),  # overrides auth_urls.login
    url(r'^accounts/', include(auth_urls)),
    url(r'^api/v0/', include(rest_urls)),
    url('', include(profile_urls)),
    url('', include('django_prometheus.urls')),
    url(r'^account-confirm-email/(?P<key>\w+)/$', ConfirmEmailView.as_view(),
        name='account_confirm_email'),
    url(r'^account-email-verification-sent/$', EmailVerificationSentView.as_view(),
        name='account_email_verification_sent'),
    url(r'^accounts/confirmed/', views.user_mail_confirmed, name='account_email_confirmed'),
    url(r'^', include(theme_urls)),
]


def authenticated_menu(request, menu_items):
    if not request.user.is_authenticated():
        return
    menu_items += (
        {
            'title': _('Your profile'),
            'view': views.user_profile,
        },
        {
            'title': _context('account', 'History'),
            'view': views.user_history,
        },
        {
            'title': _('Change profile'),
            'view': views.change_user_profile,
        },
        {
            'title': _('Logout'),
            'view': 'logout',
        }
    )


def anonymous_menu(request, menu_items):
    if request.user.is_authenticated():
        return
    menu_items += (
        {
            'title': _('Login'),
            'view': 'login',
        },
    )


def staff_menu(request, menu_items):
    if not request.user.is_staff:
        return
    menu_items.insert(-1, {
            'title': _('Admin'),
            'view': 'admin:index',
    })
