# Generated by Django 2.2.5 on 2019-09-30 09:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('qabel_provider', '0015_profile_created_on_behalf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='subscribed_plan',
            field=models.ForeignKey(default='free', on_delete=django.db.models.deletion.PROTECT, to='qabel_provider.Plan'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='profileplanlog',
            name='interval',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='qabel_provider.PlanInterval'),
        ),
        migrations.AlterField(
            model_name='profileplanlog',
            name='plan',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='qabel_provider.Plan'),
        ),
        migrations.AlterField(
            model_name='profileplanlog',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='qabel_provider.Profile'),
        ),
    ]
