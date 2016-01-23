import os
import uuid

from django.db.models import fields
from django.utils.translation import ugettext_lazy as _


class random_name_in(object):
    def __init__(self, dir):
        self.dir = dir

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = '{}.{}'.format(uuid.uuid4(), ext)
        return os.path.join(self.dir, filename)

    def deconstruct(self):
        return 'blockhunt.utils.models.random_name_in', (), {'dir': self.dir}


class CaseInsensitiveTextField(fields.TextField):
    description = _("Case insensitive text")

    def db_type(self, connection):
        return 'citext'


class CaseInsensitiveEmailField(CaseInsensitiveTextField, fields.EmailField):
    description = _("Case insensitive email address")
