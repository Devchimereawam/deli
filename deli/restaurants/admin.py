from django.contrib import admin

from .models import (
    Restaurant,
    Category,
    MenuItem,
    Inventory,
    OpeningHour,
)


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class MenuInline(admin.TabularInline):
    model = MenuItem
    extra = 0

    fields = (
        "name",
        "category",
        "price",
        "image",
        "is_available",
        "is_featured",
    )


class OpeningHourInline(admin.TabularInline):
    model = OpeningHour
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "area",
        "rating",
        "is_verified",
        "is_active",
    )

    search_fields = (
        "name",
        "phone",
        "area__name",
    )

    list_filter = (
        "is_verified",
        "is_active",
        "area",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    inlines = (
        CategoryInline,
        MenuInline,
        OpeningHourInline,
    )

    actions = ["copy_opening_hours"]

    @admin.action(description="Copy Monday hours to every day")
    def copy_opening_hours(self, request, queryset):

        for restaurant in queryset:

            monday = restaurant.opening_hours.filter(day="MON").first()

            if not monday:
                continue

            for code, _ in OpeningHour.DAYS:

                OpeningHour.objects.update_or_create(
                    restaurant=restaurant,
                    day=code,
                    defaults={
                        "opening_time": monday.opening_time,
                        "closing_time": monday.closing_time,
                        "is_closed": monday.is_closed,
                    },
                )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "restaurant",
    )

    search_fields = (
        "name",
        "restaurant__name",
    )


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "restaurant",
        "category",
        "price",
        "stock",
        "is_available",
        "is_featured",
    )

    list_filter = (
        "restaurant",
        "category",
        "is_available",
        "is_featured",
    )

    search_fields = (
        "name",
        "restaurant__name",
    )

    fields = (
        "restaurant",
        "category",
        "name",
        "description",
        "price",
        "image",
        "is_available",
        "is_featured",
    )

    readonly_fields = (
        "stock",
    )

    def stock(self, obj):
        if hasattr(obj, "inventory"):
            return obj.inventory.quantity
        return "No inventory yet"

    stock.short_description = "Current Stock"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        Inventory.objects.get_or_create(
            menu_item=obj,
        )


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):

    list_display = (
        "menu_item",
        "restaurant",
        "quantity",
        "low_stock_threshold",
        "in_stock",
        "updated_at",
    )

    list_editable = (
        "quantity",
        "low_stock_threshold",
    )

    search_fields = (
        "menu_item__name",
        "menu_item__restaurant__name",
    )

    list_filter = (
        "menu_item__restaurant",
    )

    def restaurant(self, obj):
        return obj.menu_item.restaurant

    restaurant.short_description = "Restaurant"


@admin.register(OpeningHour)
class OpeningHourAdmin(admin.ModelAdmin):

    list_display = (
        "restaurant",
        "day",
        "opening_time",
        "closing_time",
        "is_closed",
    )

    list_filter = (
        "restaurant",
        "day",
    )