from django.contrib import admin
from .models import (
    Order,
    OrderItem,
)

# Register your models here.
class OrderItemInline(admin.TabularInline):

    model = OrderItem

    extra = 0

    readonly_fields = (
        "menu_item",
        "name",
        "quantity",
        "unit_price",
        "subtotal",
        "created_at",
    )

    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "restaurant",
        "delivery_rider",
        "status",
        "subtotal",
        "delivery_fee",
        "customer_service_fee",
        "maintenance_fee",
        "total",
        "checkout_reference",
        "created_at",
    )

    list_filter = (
        "status",
        "restaurant",
        "delivery_rider",
        "created_at",
    )

    search_fields = (
        "checkout_reference",
        "payment_reference",
        "customer__phone",
        "customer__name",
        "restaurant__name",
    )

    readonly_fields = (
        "checkout_reference",
        "payment_reference",
        "checkout_url",
        "delivery_address",
        "delivery_contact_phone",
        "delivery_notes",
        "customer_service_fee",
        "maintenance_fee",
        "restaurant_platform_fee",
        "rider_platform_fee",
        "inventory_deducted_at",
        "restaurant_availability_status",
        "rider_availability_status",
        "fallback_status",
        "created_at",
        "updated_at",
    )

    inlines = [
        OrderItemInline,
    ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "order",
        "name",
        "quantity",
        "unit_price",
        "subtotal",
    )

    search_fields = (
        "name",
        "order__checkout_reference",
    )

    readonly_fields = (
        "created_at",
    )
