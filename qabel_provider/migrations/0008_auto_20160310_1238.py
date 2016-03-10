# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('qabel_provider', '0007_auto_20160225_1918'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prefix',
            name='user',
        ),
        migrations.DeleteModel(
            name='Prefix',
        ),
    ]
