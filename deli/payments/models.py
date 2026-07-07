from django.db import models
from orders.models import Order

# Create your models here.
class Payment(models.Model):

    STATUS_PENDING = "PENDING"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILED = "FAILED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
    )

    provider = models.CharField(
        max_length=30,
        default="NOMBA",
    )

    merchant_reference = models.CharField(
        max_length=100,
        unique=True,
    )

    checkout_reference = models.CharField(
        max_length=100,
        blank=True,
    )

    checkout_url = models.URLField(
        blank=True,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    currency = models.CharField(
        max_length=10,
        default="NGN",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    raw_response = models.JSONField(
        default=dict,
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

        return self.merchant_reference


class NombaWebhookEvent(models.Model):

    request_id = models.CharField(
        max_length=255,
        unique=True,
    )

    event_type = models.CharField(
        max_length=120,
        blank=True,
        default="",
    )

    payload = models.JSONField(
        default=dict,
        blank=True,
    )

    processed_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.request_id


class Payout(models.Model):

    RECIPIENT_RESTAURANT = "RESTAURANT"
    RECIPIENT_RIDER = "RIDER"

    RECIPIENT_CHOICES = [
        (RECIPIENT_RESTAURANT, "Restaurant"),
        (RECIPIENT_RIDER, "Delivery Rider"),
    ]

    STATUS_PENDING = "PENDING"
    STATUS_LOOKED_UP = "LOOKED_UP"
    STATUS_PROCESSING = "PROCESSING"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILED = "FAILED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_LOOKED_UP, "Account Looked Up"),
        (STATUS_PROCESSING, "Processing"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="payouts",
    )

    recipient_type = models.CharField(
        max_length=20,
        choices=RECIPIENT_CHOICES,
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    bank_code = models.CharField(
        max_length=20,
    )

    account_number = models.CharField(
        max_length=20,
    )

    expected_account_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    resolved_account_name = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    merchant_reference = models.CharField(
        max_length=120,
        unique=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    raw_response = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        unique_together = (
            "order",
            "recipient_type",
        )

    def __str__(self):
        return self.merchant_reference
