import os

if os.environ.get('DJANGO_SETTINGS_MODULE') == 'config.settings':
    from .default_settings import *
