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
        "status",
        "subtotal",
        "delivery_fee",
        "total",
        "checkout_reference",
        "created_at",
    )

    list_filter = (
        "status",
        "restaurant",
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