# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

API_SECRET = 'Changeme'

STATIC_URL = '/static/'

CORS_ORIGIN_WHITELIST = (
    #'qabel.dev',
)

#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.postgresql_psycopg2',
#        'NAME': 'changeme',
#        'USER': 'changeme',
#        'PASSWORD': 'changeme',
#        'HOST': 'changeme',
#        'PORT': '5432',
#    }
#}

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

#Email Settings

#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_USE_TLS = 'True'
#EMAIL_HOST = ''
#EMAIL_PORT = ''
#EMAIL_HOST_USER = ''
#EMAIL_HOST_PASSWORD = ''
#DEFAULT_FROM_EMAIL = ''
