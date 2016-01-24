from django.db import models

from model_utils.models import TimeStampedModel

from blockhunt.users.models import User


class Hunter(User):
    balance = models.DecimalField(
        max_digits=12, decimal_places=8, default=0, editable=False,
        help_text='The number of bitoins the hunter owns.'
    )
    coinbase_account_id = models.CharField(max_length=100, editable=False)


class Checkin(TimeStampedModel):
    hunter = models.ForeignKey('Hunter', related_name='checkins')
    store = models.ForeignKey('stores.Store', related_name='checkins')
    reward = models.DecimalField(max_digits=10, decimal_places=8)
