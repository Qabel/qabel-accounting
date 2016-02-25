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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

