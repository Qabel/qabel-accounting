from django.db import models
from django_prometheus.models import ExportModelOperationsMixin


class Redirect(models.Model, ExportModelOperationsMixin('redirect')):
    redirect_from = models.CharField(primary_key=True, max_length=200,
                                     help_text='Eg.: <b>buy/qabel-pro-x</b> would make the resulting link '
                                               '<i>https://accounting.qabel.org/dispatch/buy/qabel-pro-x/</i>')

    to = models.URLField()

    TYPES = (
        ('generic', 'generic link'),
        ('shareit', 'link to shareit product, cart, ... page'),
    )

    type = models.CharField(max_length=100, choices=TYPES, default='generic')

    def get_destination(self, request):
        # This allows us to do special things depending on type. For example, one may set the appropiate language
        # for some links from the referer, or add some fields (e.g. logged in account) to a shareit link.
        return self.to
