from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Sum, Count
from .models import Order, OrderItem
from menu.models import MenuItem
from datetime import datetime

@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_data(request):
    # Total Orders
    orders = Order.objects.all().order_by('-created_at')

    # Total Revenue
    total_revenue = orders.aggregate(total=Sum('total_price'))['total'] or 0

    # Top Selling Items
    top_items_qs = (
        OrderItem.objects
        .values('menu_item__id', 'menu_item__name')
        .annotate(count=Sum('quantity'))
        .order_by('-count')[:5]
    )
    top_items = [
        {'id': item['menu_item__id'], 'name': item['menu_item__name'], 'count': item['count']}
        for item in top_items_qs
    ]

    # Revenue over time (last 7 days)
    revenue_data = []
    for i in range(7, 0, -1):
        day = datetime.now().date() - timedelta(days=i)
        day_orders = orders.filter(created_at__date=day)
        day_revenue = day_orders.aggregate(total=Sum('total_price'))['total'] or 0
        revenue_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'revenue': float(day_revenue)
        })

    return Response({
        'orders': [
            {
                'id': order.id,
                'customer': order.customer.username,
                'total_price': float(order.total_price),
                'status': order.status,
                'created_at': order.created_at
            } for order in orders
        ],
        'total_revenue': float(total_revenue),
        'top_items': top_items,
        'revenue': revenue_data
    })
