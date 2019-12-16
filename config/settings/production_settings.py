from .base_settings import *
import json
ALLOWED_HOSTS = ['localhost']

DEBUG = False

# Email settings
DEFAULT_FROM_EMAIL = "noreply@qabel.de"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

LOGGING_CONFIG_FILE = os.path.join(ROOT_DIR, '..', 'logging.json')
try:
    from .local_settings import *
except ImportError:
    import sys

    print("""\
To use the production settings, create a file 'local_settings.py' in config/settings
 which defines at least the options SECRET_KEY, API_SECRET and DATABASES\
""", file=sys.stderr)
    exit(1)

with open(LOGGING_CONFIG_FILE) as config_file:
    LOGGING = json.load(config_file)
