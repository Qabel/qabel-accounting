from django.db.models import Count
from prometheus_client.core import CounterMetricFamily, REGISTRY

from .models import Profile, PlanInterval, Plan


class ProfileStatsCollector:
    def profile(self):
        c = CounterMetricFamily('profile_count', 'Number of profiles')
        c.add_metric([], Profile.objects.count())
        yield c

    def plan_interval(self):
        c = CounterMetricFamily('plan_intervals_count', 'Number of plan intervals')
        c.add_metric([], PlanInterval.objects.count())
        yield c

    def subscriptions(self):
        c = CounterMetricFamily('subscriptions_count', 'Subscriptions by plan', labels=['plan'])
        plans = Plan.objects.annotate(Count('profile'))
        for plan in plans:
            c.add_metric([plan.id], plan.profile__count)
        yield c

    def collect(self):
        yield from self.profile()
        yield from self.plan_interval()
        yield from self.subscriptions()


REGISTRY.register(ProfileStatsCollector())
