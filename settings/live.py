from .base import *

DEBUG = False
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')


# Aws
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_CUSTOM_DOMAIN = '{}.s3.amazonaws.com'.format(AWS_STORAGE_BUCKET_NAME)


# Static / media files
STATICFILES_STORAGE = 'storages_folder.backends.s3boto.StaticStorage'
STATICFILES_STORAGE_DIR = 'static'
STATIC_URL = 'https://{0}/{1}/'.format(AWS_S3_CUSTOM_DOMAIN, STATICFILES_STORAGE_DIR)
DEFAULT_FILE_STORAGE = 'storages_folder.backends.s3boto.MediaStorage'
MEDIAFILES_STORAGE_DIR = 'media'
MEDIA_URL = 'https://{0}/{1}/'.format(AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_STORAGE_DIR)


# Email
EMAIL_BACKEND = 'django_ses_backend.SESBackend'
