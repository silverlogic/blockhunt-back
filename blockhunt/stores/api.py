import re
from io import BytesIO

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

from rest_framework import mixins, viewsets, permissions, decorators, renderers
from rest_framework.response import Response

import qrcode

from .models import Store, StoreCategory
from .serializers import StoreSerializer, StoreCategorySerializer


class PngRenderer(renderers.BaseRenderer):
    media_type = 'image/png'
    format = 'png'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class StoreViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def filter_queryset(self, qs):
        coords = self.request.query_params.get('coords', None)
        if coords:
            if re.match(r'-?[\d.]+,-?[\d.]+', coords):
                y, x = coords.split(',')
                coords = Point(float(x), float(y), srid=4326)
                qs = qs.annotate(distance=Distance('address__coords', coords)).order_by('distance')
        return qs

    @decorators.detail_route(methods=['GET'], renderer_classes=[PngRenderer])
    def qrcode(self, request, *args, **kwargs):
        store = self.get_object()
        img = qrcode.make(store.pk)
        output = BytesIO()
        img.save(output)
        # import pdb; pdb.set_trace()
        return Response(output.getvalue())


class StoreCategoryViewSet(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    queryset = StoreCategory.objects.all()
    serializer_class = StoreCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
