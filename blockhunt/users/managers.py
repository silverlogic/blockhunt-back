from django.contrib.auth.models import BaseUserManager

from polymorphic.models import PolymorphicManager


class UserManager(PolymorphicManager, BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, is_superuser, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')

        user = self.model(email=email, is_active=True,
                          is_superuser=is_superuser, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, **extra_fields)
