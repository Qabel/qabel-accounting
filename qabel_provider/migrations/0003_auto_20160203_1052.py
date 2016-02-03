# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qabel_provider', '0002_prefix'),
    ]

    operations = [
        migrations.AddField(
            model_name='prefix',
            name='downloads',
            field=models.PositiveIntegerField(verbose_name='Download traffic of this user', default=0),
        ),
        migrations.AddField(
            model_name='prefix',
            name='size',
            field=models.PositiveIntegerField(verbose_name='Combined size of all files in the prefix', default=0),
        ),
        migrations.AddField(
            model_name='profile',
            name='used_storage',
            field=models.PositiveIntegerField(verbose_name='Used storage', default=0),
        ),
    ]
