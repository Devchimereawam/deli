from django.db import models
from decimal import Decimal
from django.conf import settings
from restaurants.models import Restaurant, MenuItem

# Create your models here.
class Order(models.Model):

    STATUS_PENDING = "PENDING"
    STATUS_AWAITING_PAYMENT = "AWAITING_PAYMENT"
    STATUS_PAID = "PAID"
    STATUS_ACCEPTED = "ACCEPTED"
    STATUS_PREPARING = "PREPARING"
    STATUS_ON_THE_WAY = "ON_THE_WAY"
    STATUS_DELIVERED = "DELIVERED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_AWAITING_PAYMENT, "Awaiting Payment"),
        (STATUS_PAID, "Paid"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_PREPARING, "Preparing"),
        (STATUS_ON_THE_WAY, "On The Way"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    delivery_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1000.00"),
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    payment_reference = models.CharField(
        max_length=100,
        blank=True,
    )

    checkout_reference = models.CharField(
        max_length=100,
        unique=True,
    )

    checkout_url = models.URLField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "-created_at",
        ]

    def __str__(self):

        return f"{self.checkout_reference}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.PROTECT,
    )

    name = models.CharField(
        max_length=255,
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):

        return self.name