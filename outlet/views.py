from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import Outlet
from .serializers import OutletSerializer


class OutletViewSet(viewsets.ModelViewSet):
    queryset = Outlet.objects.all()
    serializer_class = OutletSerializer

    # Anyone can GET, only staff can POST/PUT/PATCH/DELETE
    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [AllowAny()]
        return [IsAdminUser()]
