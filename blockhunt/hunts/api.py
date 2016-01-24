import logging

from django.core.urlresolvers import reverse
from django.db.models import F

from rest_framework import mixins, viewsets, permissions, decorators, status, serializers
from rest_framework.response import Response

import coinbase.wallet.error
import dj_coinbase
from requests.exceptions import HTTPError
from social.apps.django_app.utils import load_strategy, load_backend
from social.exceptions import SocialAuthBaseException
from timed_auth_token.models import TimedAuthToken

from .models import Hunter, Checkin
from .serializers import HunterSerializer, HunterFacebookSerializer, \
    CheckinSerializer, SendBitcoinSerializer


logger = logging.getLogger(__name__)


class HunterViewSet(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    queryset = Hunter.objects.all()
    serializer_class = HunterSerializer

    @decorators.list_route(methods=['POST'])
    def facebook(self, request):
        serializer = HunterFacebookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        psa_backend = 'facebook'
        access_token = serializer.data['access_token']

        redirect_uri = reverse('social:complete', args=(psa_backend,))
        social_strategy = load_strategy(request)
        psa_backend = load_backend(social_strategy, psa_backend, redirect_uri)
        try:
            user = psa_backend.do_auth(access_token)
        except SocialAuthBaseException as ex:
            return Response({'non_field_errors': [str(ex)]}, status=status.HTTP_400_BAD_REQUEST)
        except HTTPError as ex:
            logger.info('Invalid access token. %s', ex.response.json())
            return Response({'access_token': ['Invalid access token']}, status=status.HTTP_400_BAD_REQUEST)

        if user:
            return Response({'token': TimedAuthToken.objects.create(user=user).key})
        else:
            logger.info('Unkown reason for social auth failure')
            return Response({'non_field_errors': ['Something went wrong.']}, status=status.HTTP_400_BAD_REQUEST)


class HunterSelfViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset = Hunter.objects.all()
    serializer_class = HunterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(instance=user)
        return Response(serializer.data)

    @decorators.list_route(methods=['POST'], url_path='send-bitcoin')
    def send_bitcoin(self, request, *args, **kwargs):
        serializer = SendBitcoinSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            hunter = request.user
            dj_coinbase.client.send_money(
                hunter.coinbase_account_id,
                to=serializer.data['address'],
                amount=serializer.data['amount'],
                currency='BTC',
                fee='0.0001'
            )
        except coinbase.wallet.error.APIError as ex:
            raise serializers.ValidationError(ex.message)
        hunter.balance = F('balance') - serializer.data['amount']
        hunter.save()
        return Response({})


class CheckinViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Checkin.objects.all()
    serializer_class = CheckinSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(hunter=self.request.user)
        return qs
