from django.db import models
from decimal import Decimal
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

    PROVIDER_PENDING = "PENDING"
    PROVIDER_ASKED = "ASKED"
    PROVIDER_ACCEPTED = "ACCEPTED"
    PROVIDER_DECLINED = "DECLINED"
    PROVIDER_TIMEOUT = "TIMEOUT"

    PROVIDER_STATUS_CHOICES = [
        (PROVIDER_PENDING, "Pending"),
        (PROVIDER_ASKED, "Asked"),
        (PROVIDER_ACCEPTED, "Accepted"),
        (PROVIDER_DECLINED, "Declined"),
        (PROVIDER_TIMEOUT, "Timed out"),
    ]

    FALLBACK_NOT_NEEDED = "NOT_NEEDED"
    FALLBACK_OFFERED = "OFFERED"
    FALLBACK_ACCEPTED = "ACCEPTED"
    FALLBACK_DECLINED = "DECLINED"

    FALLBACK_CHOICES = [
        (FALLBACK_NOT_NEEDED, "Not needed"),
        (FALLBACK_OFFERED, "Offered"),
        (FALLBACK_ACCEPTED, "Accepted"),
        (FALLBACK_DECLINED, "Declined"),
    ]

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
        "users.Customer",
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

    customer_service_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("200.00"),
    )

    maintenance_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("100.00"),
    )

    restaurant_platform_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("200.00"),
    )

    rider_platform_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("200.00"),
    )

    delivery_rider = models.ForeignKey(
        "delivery.DeliveryRider",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )

    delivery_address = models.TextField(
        blank=True,
        default="",
    )

    delivery_contact_phone = models.CharField(
        max_length=30,
        blank=True,
        default="",
    )

    delivery_notes = models.TextField(
        blank=True,
        default="",
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

    restaurant_availability_status = models.CharField(
        max_length=20,
        choices=PROVIDER_STATUS_CHOICES,
        default=PROVIDER_PENDING,
    )

    rider_availability_status = models.CharField(
        max_length=20,
        choices=PROVIDER_STATUS_CHOICES,
        default=PROVIDER_PENDING,
    )

    restaurant_asked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    rider_asked_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    fallback_status = models.CharField(
        max_length=20,
        choices=FALLBACK_CHOICES,
        default=FALLBACK_NOT_NEEDED,
    )

    fallback_delivery_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1800.00"),
    )

    review_requested_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    inventory_deducted_at = models.DateTimeField(
        null=True,
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
