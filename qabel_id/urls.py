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
from django.conf.urls import include, url
from django.contrib import admin
from qabel_provider import views
from rest_auth.views import (
    LogoutView, UserDetailsView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView
)
from rest_auth.registration.views import VerifyEmailView
from allauth.account.views import ConfirmEmailView, EmailVerificationSentView

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
    url(r'^auth/$', views.auth_resource, name='api-auth'),
    url(r'^auth/info/$', views.info_resource, name='api-info'),
]

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^accounts/login/', 'django.contrib.auth.views.login'),
    url(r'^api/v0/', include(rest_urls)),
    url('', include('django_prometheus.urls')),
    url(r'^account-confirm-email/(?P<key>\w+)/$', ConfirmEmailView.as_view(),
        name='account_confirm_email'),
    url(r'^account-email-verification-sent/$', EmailVerificationSentView.as_view(),
        name='account_email_verification_sent'),
]
