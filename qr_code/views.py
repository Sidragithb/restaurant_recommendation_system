from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from order.models import Order  
from outlet.models import Table  

#  Main View to Handle QR Code Scan
def scan_qr_code(request, table_id):
    # Get the table object using table_id
    table = get_object_or_404(Table, number=table_id)

    # Get the last 5 orders placed at this table
    last_orders = Order.objects.filter(table=table).order_by('-created_at')[:5]

    # Extract order details
    order_history = []
    for order in last_orders:
        order_history.append({
            "order_id": order.id,
            "items": [item.name for item in order.items.all()],
            "total_price": order.total_price,
            "timestamp": order.created_at
        })

    # Generate recommendations
    recommended_items = recommend_based_on_history(last_orders)

    # Return response
    return JsonResponse({
        "table_id": table_id,
        "last_orders": order_history,
        "recommendations": recommended_items
    })

# Simple Recommendation Logic: return top 3 unique items from history
def recommend_based_on_history(last_orders):
    recommended = []
    for order in last_orders:
        for item in order.items.all():
            if item.name not in recommended:
                recommended.append(item.name)
    return recommended[:3]
