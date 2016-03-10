# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

API_SECRET = 'Changeme'

STATIC_URL = '/static/'

CORS_ORIGIN_WHITELIST = (
    #'qabel.dev',
)
CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': [
            '<host>:<port>',
            '<host>:<port>',
            '<host>:<port>',
        ],
        'OPTIONS': {
            'DB': 2,
            'PASSWORD': 'yadayada',
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