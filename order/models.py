from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from menu.models import MenuItem, SpecialOffer


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending",   "Pending"),
        ("preparing", "Preparing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    customer    = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="orders")
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.customer.username}"

    def calculate_total_price(self):
        return sum(item.unit_price * item.quantity for item in self.items.all())

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        self.total_price = self.calculate_total_price()
        super().save(update_fields=["total_price"])


class OrderItem(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item  = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity   = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.menu_item.name} × {self.quantity} (Order #{self.order_id})"

    def _discounted_unit_price(self):
        now = timezone.now()
        offer = SpecialOffer.objects.filter(
            menu_item=self.menu_item,
            valid_from__lte=now,
            valid_until__gte=now
        ).first()
        if offer:
            discount = self.menu_item.price * (offer.discount_percentage / 100)
            return self.menu_item.price - discount
        return self.menu_item.price

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self._discounted_unit_price()
        super().save(*args, **kwargs)
        self.order.total_price = self.order.calculate_total_price()
        self.order.save(update_fields=["total_price"])
