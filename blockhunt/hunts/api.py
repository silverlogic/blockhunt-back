import logging

from django.core.urlresolvers import reverse

from rest_framework import mixins, viewsets, permissions, decorators, status
from rest_framework.response import Response

from requests.exceptions import HTTPError
from social.apps.django_app.utils import load_strategy, load_backend
from social.exceptions import SocialAuthBaseException
from timed_auth_token.models import TimedAuthToken

from .models import Hunter
from .serializers import HunterSerializer, HunterFacebookSerializer


logger = logging.getLogger(__name__)


class HunterViewSet(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    queryset = Hunter.objects.all()
    serializer_class = HunterSerializer

    @decorators.list_route(methods=['POST'])
    def facebook(self, request):
        serializer = HunterFacebookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        psa_backend = 'FacebookOAuth2'
        access_token = serializer.data['access_token']

        redirect_uri = reverse('social:complete', args=(psa_backend,))
        social_strategy = load_strategy(self.context['request'])
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
