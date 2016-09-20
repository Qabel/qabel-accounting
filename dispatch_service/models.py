from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

import re


def validate_redirect_from(value):
    if value.strip() != value:
        raise ValidationError(_('Leading/trailing space is not allowed.'))
    if value.endswith('/') or value.startswith('/'):
        raise ValidationError(_('No leading/trailing slashes are allowed.'))
    if not re.match(r'^[a-zA-Z0-9_-][a-zA-Z0-9_/-]*(?<=[a-zA-Z0-9_-])$', value):
        raise ValidationError(_('Only letters, numbers, dashes (-), underscores (_) and slashes (/) are allowed.'))


class Redirect(models.Model, ExportModelOperationsMixin('redirect')):
    redirect_from = models.CharField(primary_key=True, max_length=200,
                                     help_text='Eg.: <b>buy/qabel-pro-x</b> would make the resulting link '
                                               '<i>https://accounting.qabel.org/dispatch/buy/qabel-pro-x/</i>',
                                     validators=[validate_redirect_from])

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

    def __str__(self):
        return self.redirect_from
