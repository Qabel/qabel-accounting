
from django.db.migrations.executor import MigrationExecutor
from django.db import connection

import pytest


def migrate_to(migration):
    """
    Migrate to *migration* (module name). Return Django apps configuration after migration.

    The apps can be used to fetch the modules which are valid for the migration. E.g.::

        apps = migrate_to('0002_...')
        Profile = apps.get_model('qabel_provider', 'Profile')
        p = Profile(...)
        p.save()

    For many models models() makes this easier::

        apps = migrate_to('...')
        Profile, Plan, Something, AndMore = models(apps, 'Profile', 'Plan', 'Something', 'AndMore')
    """
    migration_targets = [
        ('qabel_provider', migration)
    ]
    executor = MigrationExecutor(connection)
    executor.migrate(migration_targets)
    project_state = executor.loader.project_state(migration_targets)
    return project_state.apps


def models(apps, *models):
    """
    Return model classes from *apps* configuration for each model in *models*.
    """
    return list(apps.get_model('qabel_provider', model) for model in models)


def migrate_to_and_get_models(migration, *_models):
    return models(migrate_to(migration), *_models)

# Ok to hardcode these here, they are part of the migration
block_quota = 2 * 1024 ** 3
monthly_traffic_quota = 20 * 1024 ** 3


@pytest.mark.django_db
def test_0014_add_plans_simple(user):
    profile_pk = user.profile.pk
    Profile, = migrate_to_and_get_models('0013_profile_monthly_traffic_quota', 'Profile')

    # It's important to re-fetch the object via the migration-current model class, because a simple refresh_from_db()
    # uses the internally cached set of fields and would therefore fail.
    profile = Profile.objects.get(pk=profile_pk)

    assert profile.block_quota == block_quota
    assert profile.monthly_traffic_quota == monthly_traffic_quota

    Profile, = migrate_to_and_get_models('0014_add_plans', 'Profile')

    profile = Profile.objects.get(pk=profile_pk)
    # Another thing to know about these model objects is that they are solely constructed from the model definition
    # and don't contain any logic or properties defined beyond that (since Django doesn't have that access; it doesn't
    # require a SCM and doesn't tie DB transactions to SCM commits -- although that would be an interesting concept
    # to explore!)
    plan = profile.subscribed_plan
    assert plan.id == 'free'
    assert plan.block_quota == block_quota
    assert plan.monthly_traffic_quota == monthly_traffic_quota


@pytest.mark.django_db
def test_0014_add_plans_no_users():
    migrate_to_and_get_models('0013_profile_monthly_traffic_quota')
    Plan, = migrate_to_and_get_models('0014_add_plans', 'Plan')

    assert Plan.objects.count() == 1
    plan = Plan.objects.get(id='free')
    assert plan.block_quota == block_quota
    assert plan.monthly_traffic_quota == monthly_traffic_quota


@pytest.mark.django_db
def test_0014_add_plans_custom(user):
    profile_pk = user.profile.pk
    Profile, = migrate_to_and_get_models('0013_profile_monthly_traffic_quota', 'Profile')

    profile = Profile.objects.get(pk=profile_pk)
    profile.block_quota = 5
    profile.monthly_traffic_quota = 10
    profile.save()

    Profile, Plan = migrate_to_and_get_models('0014_add_plans', 'Profile', 'Plan')

    assert Plan.objects.count() == 2
    profile = Profile.objects.get(pk=profile_pk)
    plan = profile.subscribed_plan
    assert plan.id == 'custom-1'
    assert plan.block_quota == 5
    assert plan.monthly_traffic_quota == 10

    # The free plan is not influenced at all
    free_plan = Plan.objects.get(id='free')
    assert free_plan.block_quota == block_quota
    assert free_plan.monthly_traffic_quota == monthly_traffic_quota

    # Check back-migration
    Profile, = migrate_to_and_get_models('0013_profile_monthly_traffic_quota', 'Profile')

    profile = Profile.objects.get(pk=profile_pk)
    assert profile.block_quota == 5
    assert profile.monthly_traffic_quota == 10


@pytest.mark.django_db
def test_0014_add_plans_profile_plan_null(user):
    """Check that subscribed_plans is non-NULL after the migration."""
    profile_pk = user.profile.pk
    Profile, = migrate_to_and_get_models('0014_add_plans', 'Profile')

    profile = Profile.objects.get(pk=profile_pk)
    with pytest.raises(ValueError):
        profile.subscribed_plan = None
