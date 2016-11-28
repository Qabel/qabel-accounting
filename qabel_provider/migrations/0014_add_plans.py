from django.core.exceptions import ObjectDoesNotExist
from django.db import migrations, models
import django.db.models.deletion


def migrate_to_plans(apps, schema_editor):
    Plan = apps.get_model('qabel_provider', 'Plan')
    Profile = apps.get_model('qabel_provider', 'Profile')

    default = Plan(id='free', name='Qabel Free')
    default.save()

    for profile in Profile.objects.all():
        plan_params = {
            'block_quota': profile.block_quota,
            'monthly_traffic_quota': profile.monthly_traffic_quota,
        }
        try:
            plan = Plan.objects.get(**plan_params)
        except ObjectDoesNotExist:
            name = 'custom-%d' % Plan.objects.count()
            plan = Plan(id=name, name=name, **plan_params)
            plan.save()
        profile.subscribed_plan = plan
        profile.save()


def migrate_from_plans(apps, schema_editor):
    Profile = apps.get_model('qabel_provider', 'Profile')

    for profile in Profile.objects.all():
        plan = profile.subscribed_plan  # note that this will throw away any intervals and will *not* make them permanent
        profile.block_quota = plan.block_quota
        profile.monthly_traffic_quota = plan.monthly_traffic_quota
        profile.save()


class Migration(migrations.Migration):

    dependencies = [
        ('qabel_provider', '0013_profile_monthly_traffic_quota'),
    ]

    operations = [
        migrations.RunSQL('SET CONSTRAINTS ALL IMMEDIATE',
                          reverse_sql=migrations.RunSQL.noop),

        # (comments are for forward migration, backwards is the semantic opposite)
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.SlugField(help_text='Do not change. This is the ID used by other services to refer to this plan.', primary_key=True, serialize=False, verbose_name='internal name')),
                ('name', models.CharField(max_length=100)),
                ('block_quota', models.BigIntegerField(default=2147483648, verbose_name='block server quota (in bytes)')),
                ('monthly_traffic_quota', models.BigIntegerField(default=21474836480, verbose_name='block server traffic quota per month (in bytes)')),
            ],
            bases=(models.Model,),
        ),

        # Add NULLable subscribed_plan field to existing profiles. All profiles have now NULL here.
        migrations.AddField(
            model_name='profile',
            name='subscribed_plan',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='qabel_provider.Plan'),
        ),

        # Populate subscribed_plan fields
        migrations.RunPython(migrate_to_plans, migrate_from_plans),

        # Make it non-NULLable
        migrations.AlterField(
            model_name='profile',
            name='subscribed_plan',
            field=models.ForeignKey(default='free', on_delete=django.db.models.deletion.CASCADE, to='qabel_provider.Plan'),
        ),

        # Remove explicit per-profile quotas
        migrations.RemoveField(
            model_name='profile',
            name='block_quota',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='monthly_traffic_quota',
        ),

        # PlanInterval
        migrations.CreateModel(
            name='PlanInterval',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.DurationField()),
                ('state', models.CharField(
                    choices=[
                        ('pristine', 'pristine (neither expired nor used)'),
                        ('in_use', 'currently used interval'),
                        ('expired', 'expired interval'),
                    ], default='pristine', max_length=10)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qabel_provider.Plan')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qabel_provider.Profile')),
            ],
            options={
                'ordering': ['-id'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='planinterval',
            index_together={('profile', 'state')},
        ),

        # ProfilePlanLog
        migrations.CreateModel(
            name='ProfilePlanLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interval', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='qabel_provider.PlanInterval')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(max_length=100)),
                ('origin', models.CharField(max_length=200, verbose_name='Request origin')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qabel_provider.Plan')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='qabel_provider.Profile')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='profileplanlog',
            index_together={('timestamp',), ('profile',)},
        ),

        migrations.RunSQL(migrations.RunSQL.noop,
                          reverse_sql='SET CONSTRAINTS ALL IMMEDIATE'),
    ]
