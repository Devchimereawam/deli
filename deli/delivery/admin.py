from django.contrib import admin

from .models import DeliveryRider


@admin.register(DeliveryRider)
class DeliveryRiderAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "phone",
        "area",
        "vehicle_type",
        "base_fee",
        "rating",
        "is_available",
        "is_active",
    )

    list_filter = (
        "is_available",
        "is_active",
        "area",
        "vehicle_type",
    )

    search_fields = (
        "name",
        "phone",
        "whatsapp_number",
        "area__name",
    )
