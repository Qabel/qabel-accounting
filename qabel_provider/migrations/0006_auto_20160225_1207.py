# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qabel_provider', '0005_auto_20160215_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='plus_notification_mail',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='pro_notification_mail',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='profile',
            name='next_confirmation_mail',
            field=models.DateTimeField(null=True, verbose_name='Date of the next email confirmation', blank=True),
        ),
    ]
