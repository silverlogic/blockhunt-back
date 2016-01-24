from django.contrib.gis.geos import Point

from rest_framework import serializers

from drf_extra_fields.fields import Base64ImageField
from expander import ExpanderSerializerMixin
from geopy.geocoders import Nominatim

from blockhunt.users.models import User
from .models import Store, StoreAddress, StoreCategory, StoreOwner


class StoreCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreCategory
        fields = ('id', 'name', 'icon')


class CoordinatesField(serializers.Field):
    def to_representation(self, obj):
        return {
            'lat': obj.y,
            'long': obj.x
        }


class StoreAddressSerializer(serializers.ModelSerializer):
    coords = CoordinatesField(required=False)

    class Meta:
        model = StoreAddress
        fields = ('line1', 'line2', 'line3', 'zip_code', 'city', 'state', 'country', 'coords')


class StoreSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):
    address = StoreAddressSerializer()
    photo = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = ('id', 'name', 'category', 'address', 'photo', 'website', 'tagline',
                  'distance', 'bounty')
        expandable_fields = {
            'category': StoreCategorySerializer
        }

    def get_photo(self, obj):
        return {
            'url': obj.photo.url
        }

    def get_distance(self, obj):
        distance = getattr(obj, 'distance', None)
        if distance:
            return distance.mi


class PhotoField(serializers.Field):
    def to_representation(self, obj):
        return {
            'url': obj.url
        }

    def to_internal_value(self, data):
        if isinstance(data, str):
            return Base64ImageField().to_internal_value(data)
        return None


class StoreCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    store_name = serializers.CharField()
    category = serializers.PrimaryKeyRelatedField(queryset=StoreCategory.objects.all())
    address = StoreAddressSerializer()
    photo = PhotoField()
    website = serializers.URLField()
    tagline = serializers.CharField(required=False, allow_blank=True)
    bounty = serializers.DecimalField(max_digits=10, decimal_places=8)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('That email address is already in use.')
        return email

    def create(self, validated_data):
        store_owner = StoreOwner(email=validated_data['email'])
        store_owner.set_password(validated_data['password'])
        store_owner.save()

        store = Store.objects.create(
            owner=store_owner,
            name=validated_data['store_name'], category=validated_data['category'],
            photo=validated_data['photo'], website=validated_data['website'],
            bounty=validated_data['bounty'], tagline=validated_data.get('tagline', '')
        )

        address_data = validated_data['address']
        geolocator = Nominatim()
        location = geolocator.geocode({
            'street': '{} {} {}'.format(address_data['line1'], address_data.get('line2', ''), address_data.get('line3', '')),
            'city': address_data['city'],
            'state': address_data['state'],
            'country': address_data['country'],
            'postalcode': address_data['zip_code']
        })

        StoreAddress.objects.create(store=store, **validated_data['address'], coords=Point(location.longitude, location.latitude))
        return store

    def to_representation(self, obj):
        return StoreSerializer(instance=obj, context=self.context).data
