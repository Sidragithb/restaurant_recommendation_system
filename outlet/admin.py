from django.contrib import admin
from .models import Outlet


@admin.register(Outlet)
class OutletAdmin(admin.ModelAdmin):
    list_display  = ("id", "name", "city", "country", "status", "is_verified")
    list_filter   = ("status", "is_verified", "country")
    search_fields = ("name", "city", "owner_name", "phone_number")
    readonly_fields = ("created_at", "updated_at")
