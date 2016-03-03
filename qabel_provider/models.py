from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db.models import Sum
from django.db.transaction import atomic
from django.core import mail
from django_prometheus.models import ExportModelOperationsMixin
import uuid
import datetime
from django.utils import timezone


def confirmation_days():
    return timezone.now() + datetime.timedelta(days=7)


class Profile(models.Model, ExportModelOperationsMixin('profile')):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    quota = models.PositiveIntegerField(verbose_name="Storage quota", default=0)
    used_storage = models.PositiveIntegerField(verbose_name="Used storage", default=0)
    downloads = models.PositiveIntegerField(verbose_name="Download traffic", default=0)
    created_at = models.DateTimeField(verbose_name='Creation date and time', auto_now_add=True)
    is_confirmed = models.BooleanField(verbose_name='User confirmed profile', default=False)
    is_disabled = models.BooleanField(verbose_name='Profile is disabled', default=False)
    next_confirmation_mail = models.DateTimeField(verbose_name='Date of the next email confirmation', null=True,
                                                  blank=True)
    needs_confirmation_after = models.DateTimeField(default=confirmation_days)
    plus_notification_mail = models.BooleanField(default=False)
    pro_notification_mail = models.BooleanField(default=False)

    @property
    def prefix_downloads(self) -> int:
        result = self.user.prefix_set.aggregate(Sum('downloads'))
        return result['downloads__sum']

    def was_email_sent_last_24_hours(self) -> bool:
        return False if not self.next_confirmation_mail else self.next_confirmation_mail >= timezone.now()

    def confirmation_date_exceeded(self) -> bool:
        return self.needs_confirmation_after <= timezone.now()

    def is_allowed(self) -> bool:
        return not self.is_disabled and (self.is_confirmed
                                         or not self.confirmation_date_exceeded())

    def set_next_mail_date(self):
        self.next_confirmation_mail = timezone.now() + datetime.timedelta(hours=24)

    def check_confirmation_and_send_mail(self) -> bool:
        if not self.is_allowed():
            if not self.was_email_sent_last_24_hours():
                self.send_confirmation_mail(self.user.email)
                self.set_next_mail_date()
            self.is_disabled = True
            self.save()
            return True
        return False

    def send_confirmation_mail(self, email):
        mail.send_mail('Please confirm your e-mail address',
                       'Please confirm your e-mail address with this link:',
                       settings.DEFAULT_FROM_EMAIL, [email])


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()

