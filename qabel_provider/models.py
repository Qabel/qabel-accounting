from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db.models import Sum
from django.db.transaction import atomic
import uuid


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    quota = models.PositiveIntegerField(verbose_name="Storage quota", default=0)
    used_storage = models.PositiveIntegerField(verbose_name="Used storage", default=0)
    downloads = models.PositiveIntegerField(verbose_name="Download traffic", default=0)

    bucket = settings.BUCKET

    @property
    def prefix_downloads(self) -> int:
        result = self.user.prefix_set.aggregate(Sum('downloads'))
        return result['downloads__sum']


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()


class Prefix(models.Model):
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
