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
    'social.apps.django_app.default',
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

# Social Auth
SOCIAL_AUTH_FACEBOOK_SCOPE = ['public_profile', 'email']
SOCIAL_AUTH_FACEBOOK_KEY = env('SOCIAL_AUTH_FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = env('SOCIAL_AUTH_FACEBOOK_SECRET')
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, email, first_name, last_name'
}
SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is were emails and domains whitelists are applied (if
    # defined).
    'social.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social.pipeline.social_auth.social_user',

    # Create a user account if we haven't found one yet.
    'blockhunt.hunts.pipeline.create_hunter',

    # Create the record that associated the social account with this user.
    'social.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social.pipeline.social_auth.load_extra_data',

    # Update the user record with any changed info from the auth service.
    'social.pipeline.user.user_details',
)

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)


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
