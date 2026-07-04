from django.contrib import admin
from .models import (
    Cart,
    CartItem,
)

# Register your models here.
class CartItemInline(admin.TabularInline):

    model = CartItem

    extra = 0

    readonly_fields = (
        "subtotal",
    )

    def subtotal(self, obj):

        return obj.subtotal


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "customer",
        "total_items",
        "subtotal",
        "total",
        "updated_at",
    )

    search_fields = (
        "customer__phone",
        "customer__name",
    )

    inlines = (
        CartItemInline,
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "menu_item",
        "restaurant",
        "cart",
        "quantity",
        "subtotal",
    )

    list_filter = (
        "menu_item__restaurant",
    )

    search_fields = (
        "menu_item__name",
        "cart__customer__phone",
    )

    def restaurant(self, obj):

        return obj.menu_item.restaurant

    restaurant.short_description = "Restaurant"

    def subtotal(self, obj):

        return obj.subtotal