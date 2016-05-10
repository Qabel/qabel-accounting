from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin
from django.contrib.auth.models import User
from .models import Profile


class UserProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

    fields = (
        'plus_notification_mail', 'pro_notification_mail',
        'block_quota', 'monthly_traffic_quota'
    )


class UserAdmin(OriginalUserAdmin):
    inlines = [UserProfileInline]
    list_filter = OriginalUserAdmin.list_filter + \
        ('profile__plus_notification_mail', 'profile__pro_notification_mail')


try:
    admin.site.unregister(User)
finally:
    admin.site.register(User, UserAdmin)
