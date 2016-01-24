from django.db import IntegrityError

from social.exceptions import SocialAuthBaseException

from .models import Hunter


class EmailAlreadyExists(SocialAuthBaseException):
    def __str__(self):
        return 'User with this email already exists!'


def create_hunter(strategy, details, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    hunter = Hunter(email=details['email'],
                    first_name=details.get('first_name'),
                    last_name=details.get('last_name'))
    try:
        hunter.save()
    except IntegrityError:
        raise EmailAlreadyExists(hunter.email)

    return {
        'is_new': True,
        'user': hunter
    }
