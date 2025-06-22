from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("menu_item", "quantity")

class OrderItemReadSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.ReadOnlyField(source="menu_item.name")

    class Meta:
        model = OrderItem
        fields = ("menu_item", "menu_item_name", "quantity", "unit_price")
        read_only_fields = ("unit_price",)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemWriteSerializer(many=True, write_only=True)
    order_items = OrderItemReadSerializer(source="items", many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "status",
            "created_at",
            "total_price",
            "items",
            "order_items",
        )
        read_only_fields = ("id", "status", "created_at", "total_price")

    def create(self, validated):
        items_data = validated.pop("items", [])
        order = Order.objects.create(**validated)
        OrderItem.objects.bulk_create([
            OrderItem(order=order, **item) for item in items_data
        ])
        order.save(update_fields=["total_price"])
        return order
