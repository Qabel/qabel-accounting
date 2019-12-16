import os
import datetime
import environ

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _

ROOT_DIR = (
    environ.Path(__file__) - 3
)
env = environ.Env()
READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(ROOT_DIR.path(".env")))

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', [])

DEBUG = env.bool("DJANGO_DEBUG", False)

DATABASES = {"default": env.db("DATABASE_URL")}

# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY")

# Application definition

INSTALLED_APPS = [
    'qabel_web_theme',
    'qabel_provider',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_prometheus',
    'django_extensions',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'allauth',
    'allauth.account',
    'rest_auth.registration',
    'corsheaders',
    'axes',
    'bootstrapform',
    'nested_admin',
    'dispatch_service',
]

MIDDLEWARE = (
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'log_request_id.middleware.RequestIDMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'qabel_web_theme.middleware.MenuMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'axes.middleware.AxesMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
)

AUTHENTICATION_BACKENDS = [
    # 'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

# Login security

AXES_COOLOFF_TIME = datetime.timedelta(minutes=1)
AXES_LOGIN_FAILURE_LIMIT = 5

ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = reverse_lazy('account_email_confirmed')
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = reverse_lazy('account_email_confirmed')

ACCOUNT_EMAIL_CONFIRMATION_HMAC = False

ACCOUNT_ADAPTER = 'qabel_provider.adapters.IgnoreInvalidMailsAdapter'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOG_REQUESTS = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'request_id': {
            '()': 'log_request_id.filters.RequestIDFilter'
        }
    },
    'formatters': {
        'standard': {
            'format': '%(levelname)-8s [%(asctime)s] [%(request_id)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'filters': ['request_id'],
            'formatter': 'standard',
        },
    },
    'loggers': {
        'qabel_provider': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'axes': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i19n/

LANGUAGES = [
    ('de', _('German')),
    ('en', _('English')),
]

LANGUAGE_CODE = 'de'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# The old password is required to change it to a new password
OLD_PASSWORD_FIELD_ENABLED = True

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'qabel_provider.serializers.UserSerializer'
}

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True

# Allows, that the email address can be confirmed with a GET request
ACCOUNT_CONFIRM_EMAIL_ON_GET = True

LOGIN_REDIRECT_URL = reverse_lazy('user-profile')

MENU = (
    'config.urls.authenticated_menu',
    'config.urls.anonymous_menu',
    'config.urls.staff_menu',
)

# No trailing slash please
BLOCK_URL = 'https://block.qabel.org'
OUTGOING_REQUEST_ID_HEADER = 'X-Request-ID'

FACET_USER_PROFILE = False
