import datetime
import logging

from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction, DatabaseError
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django_prometheus.models import ExportModelOperationsMixin

logger = logging.getLogger(__name__)


def confirmation_days():
    return timezone.now() + datetime.timedelta(days=7)


class Plan(models.Model, ExportModelOperationsMixin('plan')):
    id = models.SlugField(verbose_name='internal name', primary_key=True,
                          help_text='Do not change. This is the ID used by other services to refer to this plan.')
    name = models.CharField(max_length=100)

    block_quota = models.BigIntegerField(verbose_name='block server quota (in bytes)', default=2 * 1024**3)
    monthly_traffic_quota = models.BigIntegerField(verbose_name='block server traffic quota per month (in bytes)',
                                                   default=20 * 1024**3)

    def __str__(self):
        return self.name


class Profile(models.Model, ExportModelOperationsMixin('profile')):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='Creation date and time', auto_now_add=True)
    created_on_behalf = models.BooleanField(default=False)
    next_confirmation_mail = models.DateTimeField(verbose_name='Date of the next email confirmation', null=True,
                                                  blank=True)
    needs_confirmation_after = models.DateTimeField(default=confirmation_days)
    plus_notification_mail = models.BooleanField(default=False)
    pro_notification_mail = models.BooleanField(default=False)

    # A user may only be subscribed to one plan at a time.
    # Note that subscriptions are managed outside qabel-accounting. If the subscription state
    # changes an appropriate update request is sent to the plan/subscription API.
    # The default value is constructed during the 0014_add_plans database migration.
    subscribed_plan = models.ForeignKey(Plan, default='free', on_delete=models.PROTECT)

    @property
    def plan(self):
        interval = PlanInterval.peek_interval(self)
        if interval:
            return interval.plan
        return self.subscribed_plan

    def use_plan(self):
        """Process active use of plan properties."""
        PlanInterval.get_or_start_interval(self)

    @property
    def primary_email(self):
        return EmailAddress.objects.get_primary(self.user)

    @property
    def is_confirmed(self):
        return self.primary_email.verified

    def confirm_email(self):
        email = self.primary_email
        email.verified = True
        email.save()

    def was_email_sent_last_24_hours(self) -> bool:
        if self.next_confirmation_mail is not None:
            return self.next_confirmation_mail >= timezone.now()
        else:
            return False

    def confirmation_date_exceeded(self) -> bool:
        if self.created_on_behalf:
            return False
        return self.needs_confirmation_after <= timezone.now()

    def is_allowed(self) -> bool:
        return self.user.is_active and (self.is_confirmed or not self.confirmation_date_exceeded())

    def set_next_mail_date(self):
        self.next_confirmation_mail = timezone.now() + datetime.timedelta(hours=24)

    def check_confirmation_and_send_mail(self) -> bool:
        if not self.is_allowed():
            # First we commit to the DB as-if we already sent the mail. If that fails, then another concurrent txn
            # already did this. Then we actually send the mail, if that fails, we rollback the DB manually.
            # In other words, 2PC between the DB and the mail server.
            try:
                with transaction.atomic():
                    self.refresh_from_db()
                    send_mail = not self.was_email_sent_last_24_hours()
                    if send_mail:
                        # Store original timestamp, so we can rollback manually
                        original_next_confirmation_mail = self.next_confirmation_mail
                        self.set_next_mail_date()
                        self.save()
            except DatabaseError as exc:
                logger.warning('check_confirmation_and_send_mail: raced transaction, assuming it worked for the other end: %s', str(exc))
                # Raced commit, someone else send it already.
                return True
            if send_mail:
                try:
                    self.send_confirmation_mail()
                except Exception:
                    logger.exception('Failed to send confirmation mail to user %d, email %r', self.user.pk, self.primary_email)
                    # Rollback!
                    with transaction.atomic():
                        self.next_confirmation_mail = original_next_confirmation_mail
                        self.save()
            return True
        return False

    def send_confirmation_mail(self):
        mail = self.primary_email
        logger.info('Sending confirmation mail to %r', mail.email)
        mail.send_confirmation(signup=False)
        logger.info('Sent confirmation mail to %r', mail.email)


class PlanInterval(models.Model, ExportModelOperationsMixin('planinterval')):
    # A user may own any number of (presumably prepaid) plan intervals
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)

    # Duration the interval can be used
    duration = models.DurationField()

    STATES = (
        ('pristine', 'pristine (neither expired nor used)'),
        ('in_use', 'currently used interval'),
        # expired := now() past (started_at + duration)
        ('expired', 'expired interval'),
    )
    state = models.CharField(choices=STATES, default='pristine', max_length=10)

    # Use started at <timestamp>
    started_at = models.DateTimeField(null=True, blank=True)

    def check_expiry(self):
        """
        Return false-ish if plan is expired, self otherwise.

        Update state if expired.
        """
        if self.state == 'pristine':
            raise ValueError('Cannot check expiry on pristine interval.')
        elif self.state == 'expired':
            logger.warning('PlanInterval.check_expiry on expired interval.')
            return
        if timezone.now() > (self.started_at + self.duration):
            self.state = 'expired'
            audit_log = ProfilePlanLog(profile=self.profile,
                                       action='expired-interval', plan=self.plan, interval=self)
            with transaction.atomic():
                self.save()
                audit_log.save()
            return
        return self

    def start(self):
        """Start using this (pristine) interval."""
        if self.state != 'pristine':
            raise ValueError('Cannot start using a %s interval' % self.state)
        self.state = 'in_use'
        self.started_at = timezone.now()
        audit_log = ProfilePlanLog(profile=self.profile,
                                   action='start-interval', plan=self.plan, interval=self)
        with transaction.atomic():
            self.save()
            audit_log.save()

    @classmethod
    def peek_interval(model, profile):
        """Return a plan interval for *profile* that is in use or would be used next."""
        with transaction.atomic():
            interval = model._get_interval(profile)  # The state update via check_expiry is ok
            if not interval:
                interval = model._get_pristine_interval(profile)
            return interval

    @classmethod
    def get_or_start_interval(model, profile):
        """Return/activate a plan interval for *profile*, or None."""
        with transaction.atomic():
            interval = model._get_interval(profile)
            if not interval:
                interval = model._start_interval(profile)
            return interval

    @classmethod
    def _get_interval(model, profile):
        """Return plan interval used by *profile*, or None."""
        try:
            interval = model.objects.get(profile=profile, state='in_use')
        except ObjectDoesNotExist:
            return
        else:
            return interval.check_expiry()

    @classmethod
    def _get_pristine_interval(model, profile):
        return model.objects.filter(profile=profile, state='pristine').first()

    @classmethod
    def _start_interval(model, profile):
        """Begin new plan interval for *profile*, or None if no intervals are available (anymore)."""
        usable_interval = model._get_pristine_interval(profile)
        if not usable_interval:
            return
        usable_interval.start()
        return usable_interval

    def __str__(self):
        return ''

    class Meta:
        index_together = [
            ['profile', 'state'],
        ]
        ordering = ['-id']


class ProfilePlanLog(models.Model, ExportModelOperationsMixin('profileplanlog')):
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    interval = models.ForeignKey(PlanInterval, blank=True, null=True, on_delete=models.PROTECT)

    def save(self, *args, **kwargs):
        if self.id is None:
            return super().save(*args, **kwargs)
        raise ValueError('Cannot modify existing ProfilePlanLog entry.')  # I'm sorry Dave

    def delete(self, *args, **kwargs):
        raise ValueError('Cannot delete ProfilePlanLog entry.')

    # A JsonField may be a slightly better choice here.
    origin = models.CharField(max_length=200, verbose_name='Request origin')

    def __str__(self):
        return ''

    class Meta:
        index_together = [
            ['timestamp'],
            ['profile']
        ]
        ordering = ['-timestamp']


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()
