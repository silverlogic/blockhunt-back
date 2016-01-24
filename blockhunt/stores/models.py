from django.db import models
from django.contrib.gis.db.models import PointField
from django.core.exceptions import ValidationError

from model_utils import Choices

from blockhunt.utils.models import random_name_in
from blockhunt.users.models import User


Countries = Choices(('us', 'United States'),)


class StoreOwner(User):
    pass


def validate_bounty(value):
    if value <= 0:
        raise ValidationError('Bounty must be greater than 0.')


class Store(models.Model):
    owner = models.ForeignKey('StoreOwner', related_name='stores')
    name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to=random_name_in('store-photos'))
    category = models.ForeignKey('StoreCategory', related_name='stores')
    website = models.URLField()
    tagline = models.CharField(max_length=50, blank=True)
    balance = models.DecimalField(max_digits=14, decimal_places=8, default=0)
    bounty = models.DecimalField(max_digits=10, decimal_places=8, validators=[validate_bounty])

    def __str__(self):
        return self.name


class StoreCategory(models.Model):
    name = models.CharField(max_length=30)
    icon = models.ImageField(upload_to=random_name_in('store-category-icons'))

    def __str__(self):
        return self.name


class StoreAddress(models.Model):
    store = models.OneToOneField('Store', related_name='address')
    line1 = models.CharField(max_length=100)
    line2 = models.CharField(max_length=100, blank=True)
    line3 = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, choices=Countries)
    coords = PointField(srid=4326)
