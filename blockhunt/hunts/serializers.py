import random

from django.db.models import F

from rest_framework import serializers

import dj_coinbase
from expander import ExpanderSerializerMixin

from blockhunt.stores.models import Store
from blockhunt.stores.serializers import StoreSerializer
from .models import Hunter, Checkin

names = [
    ('Bruce', 'Bitlee'),
]


class HunterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Hunter
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'balance')
        read_only_fields = ('balance',)

    def create(self, validated_data):
        if not validated_data.get('first_name') and not validated_data.get('last_name'):
            random_name = random.choice(names)
            validated_data['first_name'] = random_name[0]
            validated_data['last_name'] = random_name[1]
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class HunterFacebookSerializer(serializers.Serializer):
    access_token = serializers.CharField()


class CheckinSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    qrcode = serializers.CharField(write_only=True)

    class Meta:
        model = Checkin
        fields = ('id', 'store', 'reward', 'qrcode')
        expandable_fields = {
            'store': (StoreSerializer, (), {'read_only': True})
        }
        read_only_fields = ('store', 'reward',)

    def validate_qrcode(self, qrcode):
        store_id = int(qrcode)
        self.store = store = Store.objects.get(pk=store_id)
        if store.balance < store.bounty:
            raise serializers.ValidationError('Unfortunately the store does not have enough bitcoins to pay the bounty.')
        return qrcode

    def create(self, validated_data):
        store = self.store

        hunter = self.context['request'].user
        if not hunter.coinbase_account_id:
            coinbase_account = dj_coinbase.client.create_account(name='Hunter #' + str(hunter.pk))
            hunter.coinbase_account_id = coinbase_account.id

        dj_coinbase.client.transfer_money(
            store.coinbase_account_id,
            to=hunter.coinbase_account_id,
            amount=store.bounty,
            currency='BTC'
        )
        checkin = Checkin.objects.create(store=store,
                                         reward=store.bounty,
                                         hunter=hunter)
        hunter.balance = F('balance') + store.bounty
        hunter.save()
        store.balance = F('balance') - store.bounty
        store.save()
        return checkin


class SendBitcoinSerializer(serializers.Serializer):
    address = serializers.CharField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=8)

    def validate_amount(self, amount):
        hunter = self.context['request'].user
        if amount > hunter.balance:
            raise serializers.ValidationError('You don\'t own that many bitcoins.')
        if amount <= 0:
            raise serializers.ValidationError('You cannot send that many bitcoins.')
        return amount
