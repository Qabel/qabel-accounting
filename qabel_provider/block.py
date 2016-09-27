import logging

from django.conf import settings

from log_request_id.session import Session

from rest_auth.app_settings import create_token
from rest_auth.models import TokenModel


module_logger = logging.getLogger(__name__)

BASE_URL = settings.BLOCK_URL + '/api/v0/'


def check_response(response, logger=None, ok_codes=(200,)):
    """Raise exception if *response.status_code* is not in *ok_codes*."""
    if response.status_code in ok_codes:
        return
    if logger:
        try:
            reason = response.json()
        except:
            reason = response.text
        logger.error('Request failed (status code %d): %s', response.status_code, reason)
    response.raise_for_status()
    raise ValueError('Request failed with status code %d', response.status_code)


def get_block_quota_of_user(user):
    logger = module_logger.getChild('get_block_quota_of_user')
    logger.info('Retrieving quota of user %r on %r', user.username, settings.BLOCK_URL)
    response = Session().get(BASE_URL + 'quota/', headers={
        'Authorization': 'Token %s' % create_token(TokenModel, user, None),
    })
    check_response(response, logger)
    quota = response.json()
    logger.info('Received quota: %r', quota)
    return quota['quota'], quota['size']
