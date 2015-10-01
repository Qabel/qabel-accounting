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

# noinspection PyCallByClass
user = views.UserViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
})

# noinspection PyCallByClass
profile = views.ProfileViewSet.as_view({
    'get': 'retrieve',
})

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url('^accounts/', include('django.contrib.auth.urls')),
    url('^accounts/profile', views.profile),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v0/profile', profile),
    url(r'^api/v0/user', user),
]
