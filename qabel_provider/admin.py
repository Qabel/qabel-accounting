from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as OriginalUserAdmin
from django.contrib.auth.models import User

import nested_admin

from .models import Profile, Plan, PlanInterval, ProfilePlanLog


class PlanIntervalInline(nested_admin.NestedTabularInline):
    model = PlanInterval
    can_delete = False
    extra = 1

    fields = (
        'plan', 'duration', 'state', 'started_at',
    )


class ProfilePlanLogInline(nested_admin.NestedTabularInline):
    model = ProfilePlanLog
    extra = 0
    can_delete = False

    def has_add_permission(self, request):
        return False

    fields = (
        'timestamp', 'action', 'plan', 'interval',
    )
    readonly_fields = fields
    # This is basically just a table now; no adding, deleting or modifying of records in the admin.


class UserProfileInline(nested_admin.NestedStackedInline):
    inlines = [PlanIntervalInline, ProfilePlanLogInline]
    model = Profile
    can_delete = False

    fields = (
        'plus_notification_mail', 'pro_notification_mail',
        'subscribed_plan',
    )


class UserAdmin(OriginalUserAdmin, nested_admin.NestedModelAdmin):
    inlines = [UserProfileInline]
    list_filter = OriginalUserAdmin.list_filter + \
        ('profile__plus_notification_mail', 'profile__pro_notification_mail')


class PlanAdmin(admin.ModelAdmin):
    model = Plan

    fields = (
        'id', 'name', 'block_quota', 'monthly_traffic_quota',
    )

try:
    admin.site.unregister(User)
finally:
    admin.site.register(User, UserAdmin)
admin.site.register(Plan, PlanAdmin)
