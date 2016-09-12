from datetime import timedelta
from django.utils import timezone

import pytest

from .models import PlanInterval, ProfilePlanLog
from .test_rest import best_plan


def test_user(user):
    """ Check that we have a profile
    """
    assert not user.is_staff


def test_superuser(admin_user):
    assert admin_user.is_staff


def test_profile_is_not_confirmed_but_allowed(profile):
    assert profile.is_allowed()


def test_profile_is_confirmed_and_allowed(profile):
    profile.confirm_email()
    profile.save()
    profile.refresh_from_db()
    assert profile.is_allowed()


def test_profile_is_disabled(profile):
    profile.user.is_active = False
    profile.user.save()
    profile.refresh_from_db()
    assert not profile.is_allowed()

    profile.confirm_email()
    profile.save()
    profile.refresh_from_db()
    assert not profile.is_allowed()


def test_profile_is_not_confirmed_and_confirmation_date_exceeded(profile):
    profile.needs_confirmation_after = timezone.now()
    profile.save()
    profile.refresh_from_db()
    assert not profile.is_allowed()


def test_email_sent_1_day_ago(profile):
    profile.email_confirmation_date = timezone.now() - timedelta(days=1)
    profile.save()
    profile.refresh_from_db()
    assert not profile.was_email_sent_last_24_hours()


class TestPlanInterval:
    @pytest.fixture
    def interval(self, user, best_plan):
        interval = PlanInterval(profile=user.profile,
                                plan=best_plan,
                                duration=timedelta(days=1))
        interval.save()
        return interval

    @pytest.fixture
    def profile_plan_log(self, user):
        return ProfilePlanLog.objects.filter(profile=user.profile)

    def test_check_expiry_pristine(self, interval):
        with pytest.raises(ValueError):
            interval.check_expiry()

    def test_check_expiry_expired(self, interval):
        interval.state = 'expired'
        assert not interval.check_expiry()

    def test_check_expiry_is_exact(self, interval, monkeypatch):
        interval.start()
        assert interval.state == 'in_use'
        assert interval.check_expiry() is interval

        into_the_future = interval.started_at + timedelta(days=1)
        monkeypatch.setattr(timezone, 'now', lambda: into_the_future)
        assert interval.check_expiry()

        monkeypatch.setattr(timezone, 'now', lambda: into_the_future + timedelta(microseconds=1))
        assert not interval.check_expiry()
        assert interval.state == 'expired'

    def test_started_at(self, interval):
        assert interval.started_at is None
        interval.start()
        assert interval.started_at

    @pytest.mark.parametrize('state', ('in_use', 'expired',))
    def test_start_non_pristine(self, interval, state, profile_plan_log):
        interval.state = state
        with pytest.raises(ValueError):
            interval.start()
        assert interval.state == state
        assert not interval.started_at
        assert not profile_plan_log

    def test_start_audit_log(self, interval, profile_plan_log, best_plan):
        assert not profile_plan_log
        interval.start()
        log = profile_plan_log.get()
        assert log.plan == best_plan
        assert log.interval == interval
        assert log.action == 'start-interval'

    def test_check_expiry_audit_log(self, interval, profile_plan_log, best_plan, monkeypatch):
        assert not profile_plan_log
        interval.start()

        into_the_future = interval.started_at + timedelta(days=2)
        monkeypatch.setattr(timezone, 'now', lambda: into_the_future)

        profile_plan_log.delete()  # clear old entry
        assert not interval.check_expiry()
        log = profile_plan_log.get()
        assert log.plan == best_plan
        assert log.interval == interval
        assert log.action == 'expired-interval'
