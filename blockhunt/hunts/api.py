from rest_framework import mixins, viewsets, permissions, response

from .models import Hunter
from .serializers import HunterSerializer


class HunterViewSet(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    queryset = Hunter.objects.all()
    serializer_class = HunterSerializer


class HunterSelfViewSet(mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset = Hunter.objects.all()
    serializer_class = HunterSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(instance=user)
        return response.Response(serializer.data)
