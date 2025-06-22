from django.db import models
from django.urls import reverse
from qr_code.utils import generate_qr_code    # ← same helper we wrote earlier


#  Outlet  (restaurant, cafe, etc.)
class Outlet(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    # basic info
    name          = models.CharField(max_length=150)
    owner_name    = models.CharField(max_length=120, blank=True)
    street_number = models.CharField(max_length=50,  blank=True)
    address       = models.CharField(max_length=255, blank=True)   
    city          = models.CharField(max_length=80)
    country       = models.CharField(max_length=60)
    postal_code   = models.CharField(max_length=20, blank=True)

    # geo / status
    latitude      = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude     = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    is_verified   = models.BooleanField(default=False)

    # media / contact
    avatar        = models.URLField(blank=True)
    phone_number  = models.CharField(max_length=30, blank=True)

    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


#  Table  (per‑outlet QR‑code)

class Table(models.Model):
    outlet   = models.ForeignKey(Outlet, on_delete=models.CASCADE, related_name="tables")
    number   = models.PositiveIntegerField()
    qr_code  = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    class Meta:
        unique_together = ("outlet", "number")
        ordering        = ["outlet", "number"]

    def __str__(self):
        return f"{self.outlet.name} -  Table {self.number}"


    def get_scan_url(self):
        return reverse("scan-table", args=[self.pk])

    def save(self, *args, **kwargs):
        creating = self.pk is None
        super().save(*args, **kwargs)            
        if creating or not self.qr_code:
            self.qr_code = generate_qr_code(self.get_scan_url())
            super().save(update_fields=["qr_code"])
