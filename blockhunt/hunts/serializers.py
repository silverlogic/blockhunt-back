import random

from rest_framework import serializers

from .models import Hunter

names = [
    ('Bruce', 'Bitlee'),
]


class HunterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Hunter
        fields = ('id', 'email', 'password', 'first_name', 'last_name')

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
