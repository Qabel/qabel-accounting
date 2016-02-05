# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qabel_provider', '0003_auto_20160203_1052'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='downloads',
            field=models.PositiveIntegerField(verbose_name='Download traffic', default=0),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='downloads',
            field=models.PositiveIntegerField(verbose_name='Download traffic from this prefix', default=0),
        ),
    ]
