from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin
from django.contrib.auth.models import User
from .models import Profile, Prefix


class UserProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class UserPrefixInline(admin.StackedInline):
    model = Prefix
    can_delete = False


class UserAdmin(OriginalUserAdmin):
    inlines = [UserProfileInline, UserPrefixInline]

try:
    admin.site.unregister(User)
finally:
    admin.site.register(User, UserAdmin)
