from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('qabel_provider', '0014_add_plans'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='created_on_behalf',
            field=models.BooleanField(default=False),
        ),
    ]
