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

    bucket = settings.BUCKET

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


class Prefix(models.Model, ExportModelOperationsMixin('prefix')):
    user = models.ForeignKey(User)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    size = models.PositiveIntegerField(
        verbose_name="Combined size of all files in the prefix", default=0)
    downloads = models.PositiveIntegerField(
        verbose_name="Download traffic from this prefix", default=0
    )

    @classmethod
    def get_by_name(cls, name: str):
        try:
            prefix_id = uuid.UUID(name)
        except ValueError:
            raise Prefix.DoesNotExist("Prefix {} could not be converted to UUID".format(repr(name)))
        return cls.objects.get(id=prefix_id)

    def __str__(self):
        return str(self.id)


def handle_request(method: str, size: int, prefix: Prefix, user: User):
    size = int(size)
    with atomic():
        if method == 'store':
            handle_store(size, prefix, user)
        elif method == 'get':
            handle_get(size, prefix, user)
        else:
            raise TypeError("Method {} not recognized".format(repr(method)))


def handle_store(size: int, prefix: Prefix, user: User):
    profile = user.profile
    profile.used_storage += size
    profile.save()
    prefix.size += size
    prefix.save()


def handle_get(size: int, prefix: Prefix, user: User):
    if size < 0:
        raise ValueError('Cannot remove download traffic')
    prefix.downloads += size
    prefix.save()
    profile = user.profile
    profile.downloads += size
    profile.save()
