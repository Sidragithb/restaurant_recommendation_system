from rest_framework import serializers
from menu.models import MenuItem

class MenuItemMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ["id", "name", "price", "average_rating"]
