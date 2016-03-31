from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_prometheus.models import ExportModelOperationsMixin
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
    next_confirmation_mail = models.DateTimeField(verbose_name='Date of the next email confirmation', null=True,
                                                  blank=True)
    needs_confirmation_after = models.DateTimeField(default=confirmation_days)
    plus_notification_mail = models.BooleanField(default=False)
    pro_notification_mail = models.BooleanField(default=False)

    @property
    def is_confirmed(self):
        email = EmailAddress.objects.get_primary(self.user)
        return email.verified

    def confirm_email(self):
        email = EmailAddress.objects.get_primary(self.user)
        email.verified = True
        email.save()

    def was_email_sent_last_24_hours(self) -> bool:
        if self.next_confirmation_mail is not None:
            return self.next_confirmation_mail >= timezone.now()
        else:
            return False

    def confirmation_date_exceeded(self) -> bool:
        return self.needs_confirmation_after <= timezone.now()

    def is_allowed(self) -> bool:
        return self.user.is_active and \
               (self.is_confirmed or not self.confirmation_date_exceeded())

    def set_next_mail_date(self):
        self.next_confirmation_mail = timezone.now() + datetime.timedelta(hours=24)

    def check_confirmation_and_send_mail(self) -> bool:
        if not self.is_allowed():
            if not self.was_email_sent_last_24_hours():
                self.send_confirmation_mail()
                self.set_next_mail_date()
            self.save()
            return True
        return False

    def send_confirmation_mail(self):
        EmailAddress.objects.get_primary(self.user).send_confirmation(signup=False)


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()

