import re
from io import BytesIO

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db.models import F

from rest_framework import mixins, viewsets, permissions, decorators, renderers
from rest_framework.response import Response

import dj_coinbase
import qrcode

from .models import Store, StoreCategory
from .serializers import StoreSerializer, StoreCategorySerializer, StoreCreateSerializer


class MultiSerializerMixin:
    '''Allows a different serializer class for each view action.

    To control what serializer gets used override the serializer_class dict.  The key
    is the action name and the value is the serializer class.  If the action is not
    specified then it will use `self.serializer_class`.

    The default actions are:
        - create
        - retrieve
        - update
        - partial_update
        - list

    '''
    serializer_classes = {}

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.serializer_class)


class PngRenderer(renderers.BaseRenderer):
    media_type = 'image/png'
    format = 'png'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data


class IsStoreOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class StoreViewSet(MultiSerializerMixin,
                   mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    serializer_classes = {
        'create': StoreCreateSerializer
    }

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
        return Response(output.getvalue())

    @decorators.detail_route(methods=['POST'], permission_classes=[permissions.IsAuthenticated, IsStoreOwner])
    def load_bitcoins(self, request, *args, **kwargs):
        store = self.get_object()
        if not store.coinbase_account_id:
            coinbase_account = dj_coinbase.client.create_account(name='Store #' + str(store.pk))
            store.coinbase_account_id = coinbase_account.id
            store.save()

        coinbase_address = dj_coinbase.client.create_address(store.coinbase_account_id)
        return Response({'address': coinbase_address.address})


class CoinbaseNotificationViewSet(mixins.CreateModelMixin,
                                  viewsets.GenericViewSet):
    def create(self, request, *args, **kwargs):
        data = request.data
        print(data)
        if data['type'] == dj_coinbase.NotificationType.ADDRESS_PAYMENT:
            coinbase_account_id = data['account']['id']
            store = Store.objects.get(coinbase_account_id=coinbase_account_id)
            store.balance = F('balance') + data['data']['amount']['amount']
            store.save()
        return Response()


class StoreCategoryViewSet(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    queryset = StoreCategory.objects.all()
    serializer_class = StoreCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
