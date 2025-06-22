from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OutletViewSet

router = DefaultRouter()
router.register(r"outlets", OutletViewSet, basename="outlet")

urlpatterns = [
    path("", include(router.urls)),
]
