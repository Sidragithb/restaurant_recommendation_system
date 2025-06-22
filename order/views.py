from rest_framework import viewsets, serializers, permissions
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    OrderItemWriteSerializer,
    OrderItemReadSerializer
)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Order.objects.order_by("-created_at")
        return qs if self.request.user.is_staff else qs.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class OrderItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = OrderItem.objects.select_related("order", "menu_item")
        return qs if self.request.user.is_staff else qs.filter(order__customer=self.request.user)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return OrderItemReadSerializer
        return OrderItemWriteSerializer

    def perform_create(self, serializer):
        order_id = self.request.data.get("order")
        if not order_id:
            raise serializers.ValidationError({"order": "Order ID is required."})

        try:
            if self.request.user.is_staff:
                order = Order.objects.get(id=order_id)
            else:
                order = Order.objects.get(id=order_id, customer=self.request.user)
        except Order.DoesNotExist:
            raise serializers.ValidationError({"order": "Order not found or not yours."})

        serializer.save(order=order)
