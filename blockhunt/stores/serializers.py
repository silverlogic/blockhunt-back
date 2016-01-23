from rest_framework import serializers

from expander import ExpanderSerializerMixin

from .models import Store, StoreAddress, StoreCategory


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
    coords = CoordinatesField()

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
                  'distance')
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
