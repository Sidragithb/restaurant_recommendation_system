# serializers.py
from rest_framework import serializers
from .models import Order, OrderItem, MenuItem  # ensure MenuItem imported

# Serializer for creating/updating order items
class OrderItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("menu_item", "quantity")

# Serializer for reading order items
class OrderItemReadSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.ReadOnlyField(source="menu_item.name")
    unit_price = serializers.ReadOnlyField(source="menu_item.price")

    class Meta:
        model = OrderItem
        fields = ("menu_item", "menu_item_name", "quantity", "unit_price")

# Main Order serializer
class OrderSerializer(serializers.ModelSerializer):
    # write-only nested items
    items = OrderItemWriteSerializer(many=True, write_only=True)
    # read-only nested items
    order_items = OrderItemReadSerializer(source="items", many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "user",
            "status",
            "created_at",
            "total_price",
            "items",
            "order_items",
        )
        read_only_fields = ("id", "status", "created_at", "total_price", "user")

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        user = self.context["request"].user  # associate order with logged-in user
        order = Order.objects.create(user=user, **validated_data)

        # Create OrderItems
        order_items = []
        total = 0
        for item in items_data:
            menu_item = item["menu_item"]
            quantity = item["quantity"]
            order_item = OrderItem(order=order, menu_item=menu_item, quantity=quantity)
            order_items.append(order_item)
            total += menu_item.price * quantity

        OrderItem.objects.bulk_create(order_items)

        # Save total price
        order.total_price = total
        order.save(update_fields=["total_price"])

        return order
