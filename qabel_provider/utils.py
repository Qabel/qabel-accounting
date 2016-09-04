
from django.utils.text import Truncator


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
