from .base_settings import *

DEBUG = False

# Email settings
DEFAULT_FROM_EMAIL = "noreply@qabel.de"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

try:
    from .local_settings import *
except ImportError:
    import sys
    print("""\
To use the production settings, create a file 'local_settings.py' in qabel_id/settings
 which defines at least the options SECRET_KEY, API_SECRET and DATABASES\
""", file=sys.stderr)
    exit(1)

