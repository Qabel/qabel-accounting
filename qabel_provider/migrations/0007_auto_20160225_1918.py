# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qabel_provider', '0006_auto_20160224_1256'),
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
    ]
