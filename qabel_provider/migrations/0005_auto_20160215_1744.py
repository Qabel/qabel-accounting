# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import qabel_provider.models


class Migration(migrations.Migration):

    dependencies = [
        ('qabel_provider', '0004_auto_20160203_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='created_at',
            field=models.DateTimeField(verbose_name='Creation date and time', auto_now_add=True, default=datetime.datetime(2016, 2, 15, 17, 44, 34, 944062, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='is_confirmed',
            field=models.BooleanField(verbose_name='User confirmed profile', default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_disabled',
            field=models.BooleanField(verbose_name='Profile is disabled', default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='needs_confirmation_after',
            field=models.DateTimeField(default=qabel_provider.models.confirmation_days),
        ),
        migrations.AddField(
            model_name='profile',
            name='next_confirmation_mail',
            field=models.DateTimeField(null=True, verbose_name='Date of the last email confirmation', blank=True),
        ),
    ]
