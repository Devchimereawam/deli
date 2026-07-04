from django.contrib import admin
from .models import Payment

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