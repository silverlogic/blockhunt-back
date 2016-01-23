from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import ugettext as _

from model_utils.models import TimeStampedModel
from polymorphic.models import PolymorphicModel

from blockhunt.utils.models import CaseInsensitiveEmailField
from .managers import UserManager


class PermissionsMixin(models.Model):
    '''
    A mixin class that adds the fields and methods necessary to support
    Django's Permission model using the ModelBackend.
    '''
    is_superuser = models.BooleanField(
        _('superuser status'), default=False,
        help_text=_('Designates that this user has all permissions without '
                    'explicitly assigning them.')
    )

    class Meta:
        abstract = True

    def has_perm(self, perm, obj=None):
        '''
        Returns True if the user is superadmin and is active
        '''
        return self.is_active and self.is_superuser

    def has_perms(self, perm_list, obj=None):
        '''
        Returns True if the user is superadmin and is active
        '''
        return self.is_active and self.is_superuser

    def has_module_perms(self, app_label):
        '''
        Returns True if the user is superadmin and is active
        '''
        return self.is_active and self.is_superuser

    @property
    def is_staff(self):
        return self.is_superuser


class User(TimeStampedModel, AbstractBaseUser, PermissionsMixin, PolymorphicModel):
    email = CaseInsensitiveEmailField(unique=True)
    first_name = models.CharField(blank=True, max_length=50)
    last_name = models.CharField(blank=True, max_length=50)

    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.')
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_short_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def get_full_name(self):
        return self.get_short_name()
