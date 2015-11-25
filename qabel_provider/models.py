from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
import uuid


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    quota = models.PositiveIntegerField(verbose_name="Storage quota", default=0)

    bucket = settings.BUCKET


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()


class Prefix(models.Model):
    user = models.ForeignKey(User)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.id)