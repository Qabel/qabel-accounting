import os

from django.utils.text import Truncator
from django.contrib.auth.models import User

from allauth.utils import get_username_max_length


def elide(string, length):
    if length:
        return Truncator(string).chars(length)
    else:
        return string


def get_request_origin(request, max_length=None):
    meta = request.META
    origin = []
    user = meta.get('REMOTE_USER')
    if user:
        origin.append('user %r' % user)

    addr = meta.get('REMOTE_ADDR')
    if addr:
        origin.append('address %r' % addr)

    host = meta.get('REMOTE_HOST')
    if host:
        origin.append('host %r' % host)

    origin = ', '.join(origin)
    return elide(origin, max_length)


def gen_username(email):
    mailbox, domain = email.rsplit('@', maxsplit=1)
    username = mailbox
    n = 1
    while User.objects.filter(username=username).count():
        username = '%s%d' % (mailbox, n)
        n += 1

    max_length = get_username_max_length()
    if max_length and len(username) > max_length:
        # I give up.
        return os.urandom(max_length // 2).hex()

    return username
