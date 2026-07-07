from decimal import Decimal

from django.db import models


class DeliveryRider(models.Model):

    name = models.CharField(
        max_length=255,
    )

    phone = models.CharField(
        max_length=30,
        unique=True,
    )

    whatsapp_number = models.CharField(
        max_length=30,
        blank=True,
        default="",
    )

    area = models.ForeignKey(
        "locations.Area",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="delivery_riders",
    )

    vehicle_type = models.CharField(
        max_length=80,
        blank=True,
        default="Bike",
    )

    base_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1500.00"),
    )

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal("5.00"),
    )

    total_reviews = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_available = models.BooleanField(
        default=True,
    )

    bank_name = models.CharField(
        max_length=120,
        blank=True,
        default="",
    )

    bank_code = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    account_number = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    account_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-rating",
            "base_fee",
            "name",
        ]

    @property
    def whatsapp_phone(self):
        return self.whatsapp_number or self.phone

    def __str__(self):
        return self.name
