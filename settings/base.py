import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

import dj_database_url


def env(var_name):
    '''Get the environment variable or raise exception.'''
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the {} environment variable".format(var_name)
        raise ImproperlyConfigured(error_msg)


BASE_DIR = Path(__file__).parent.parent
APPS_DIR = BASE_DIR / 'blockhunt'

ALLOWED_HOSTS = ['*']
ROOT_URLCONF = 'blockhunt.urls'
WSGI_APPLICATION = 'blockhunt.wsgi.application'
SECRET_KEY = env('SECRET_KEY')
AUTH_USER_MODEL = 'users.User'


DATABASES = {
    'default': dj_database_url.config()
}


# Applications
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.gis',
]
THIRD_PARTY_APPS = [
    'rest_framework',
    'timed_auth_token',
    'polymorphic',
]
PROJECT_APPS = [
    'blockhunt.users',
    'blockhunt.stores',
    'blockhunt.hunts',
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS


MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


AUTH_PASSWORD_VALIDATORS = [
]


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [str(APPS_DIR / 'templates')],
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


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images) and media files (user uploads)
# These are overriden in production to use Amazon S3
STATIC_URL = '/static/'
STATIC_ROOT = str(BASE_DIR / 'static')
MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR / 'media')


# Rest framework
REST_FRAMEWORK = {
    # 'DEFAULT_FILTER_BACKENDS': [
    #     'rest_framework.filters.DjangoFilterBackend',
    # ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        # Used for API clients.
        'timed_auth_token.authentication.TimedAuthTokenAuthentication',

        # Used for browsable API.
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'SEARCH_PARAM': 'q',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}
