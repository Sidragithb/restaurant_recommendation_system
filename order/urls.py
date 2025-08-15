from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItemViewSet
from .views_dashboard import dashboard_data 


router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet, basename='orderitem')


urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', dashboard_data, name='dashboard-data'),
    
]
