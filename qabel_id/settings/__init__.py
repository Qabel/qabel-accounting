import os

if os.environ.get('DJANGO_SETTINGS_MODULE') == 'qabel_id.settings':
    from .default_settings import *