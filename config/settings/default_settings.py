from .base_settings import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=tmcici-p92_^_jih9ud11#+wb7*i21firlrtcqh$p+d7o*49@'
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY")


API_SECRET = env('API_SECRET')

# Email settings
DEFAULT_FROM_EMAIL = "noreply@qabel.de"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(ROOT_DIR, 'staticfiles')
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': [
            'localhost:6379',
        ],
        'OPTIONS': {
            'DB': 1,
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'CONNECTION_POOL_CLASS': 'redis.BlockingConnectionPool',
            'CONNECTION_POOL_CLASS_KWARGS': {
                'max_connections': 50,
                'timeout': 20,
            },
            'MAX_CONNECTIONS': 1000,
            'PICKLE_VERSION': -1,
        },
    },
}
