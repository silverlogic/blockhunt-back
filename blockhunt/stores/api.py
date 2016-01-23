import re

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

from rest_framework import mixins, viewsets, permissions

from .models import Store, StoreCategory
from .serializers import StoreSerializer, StoreCategorySerializer


class StoreViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def filter_queryset(self, qs):
        coords = self.request.query_params.get('coords', None)
        if coords:
            if re.match(r'[\d.]+,[\d.]+', coords):
                y, x = coords.split(',')
                coords = Point(float(x), float(y), srid=4326)
                qs = qs.annotate(distance=Distance('address__coords', coords)).order_by('distance')
        return qs


class StoreCategoryViewSet(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    queryset = StoreCategory.objects.all()
    serializer_class = StoreCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
