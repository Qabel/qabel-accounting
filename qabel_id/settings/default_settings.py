from .base_settings import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=tmcici-p92_^_jih9ud11#+wb7*i21firlrtcqh$p+d7o*49@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

API_SECRET = 'Changeme'

# Email settings
DEFAULT_FROM_EMAIL = "noreply@qabel.de"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'qabel_index',
        'USER': 'qabel',
        'PASSWORD': 'qabel_test',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

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
