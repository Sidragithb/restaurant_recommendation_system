from rest_framework import serializers
from .models import Outlet


class OutletSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Outlet
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
