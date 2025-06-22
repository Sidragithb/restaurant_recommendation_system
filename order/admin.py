from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price',)  # Show unit_price as readonly in the inline form


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ('id', 'customer', 'status', 'total_price', 'created_at')
    list_filter   = ('status', 'created_at')
    search_fields = ('customer__username',)
    autocomplete_fields = ('customer',)       
    inlines = [OrderItemInline]

    def get_readonly_fields(self, request, obj=None):
        common = ('total_price', 'created_at')
        return common if obj is None else ('customer',) + common


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display  = ('id', 'order', 'menu_item', 'quantity', 'unit_price')
    readonly_fields = ('unit_price',)
    list_filter   = ('menu_item',)
    search_fields = ('menu_item__name', 'order__customer__username')
