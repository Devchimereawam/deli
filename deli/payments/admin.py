from django.contrib import admin
from .models import (
    NombaWebhookEvent,
    Payment,
    Payout,
)

# Register your models here.
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "merchant_reference",
        "order",
        "provider",
        "amount",
        "currency",
        "status",
        "paid_at",
        "created_at",
    )

    list_filter = (
        "status",
        "provider",
        "created_at",
    )

    search_fields = (
        "merchant_reference",
        "checkout_reference",
        "order__checkout_reference",
        "order__customer__phone",
        "order__customer__name",
    )

    readonly_fields = (
        "merchant_reference",
        "checkout_reference",
        "checkout_url",
        "provider",
        "amount",
        "currency",
        "raw_response",
        "paid_at",
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )


@admin.register(NombaWebhookEvent)
class NombaWebhookEventAdmin(admin.ModelAdmin):

    list_display = (
        "request_id",
        "event_type",
        "processed_at",
    )

    search_fields = (
        "request_id",
        "event_type",
    )

    readonly_fields = (
        "request_id",
        "event_type",
        "payload",
        "processed_at",
    )


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):

    list_display = (
        "merchant_reference",
        "order",
        "recipient_type",
        "amount",
        "status",
        "resolved_account_name",
        "updated_at",
    )

    list_filter = (
        "recipient_type",
        "status",
        "created_at",
    )

    search_fields = (
        "merchant_reference",
        "order__checkout_reference",
        "account_number",
        "expected_account_name",
        "resolved_account_name",
    )

    readonly_fields = (
        "merchant_reference",
        "raw_response",
        "created_at",
        "updated_at",
    )
