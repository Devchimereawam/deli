from django.contrib import admin

from .models import Customer, ConversationState


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "phone",
        "default_address",
        "account_type",
        "is_registered",
        "created_at",
    )

    list_filter = (
        "account_type",
        "is_registered",
    )

    search_fields = (
        "phone",
        "name",
    )
    
    def default_address(self, obj):
        address = obj.addresses.filter(is_default=True).first()

        if address:
            return address.formatted_address

        return "-"

    default_address.short_description = "Default Address"


@admin.register(ConversationState)
class ConversationAdmin(admin.ModelAdmin):

    list_display = (
        "customer",
        "current_step",
        "selected_restaurant",
        "selected_category",
        "selected_menu_item",
        "search_query",
        "updated_at",
    )

    list_filter = (
        "current_step",
        "selected_restaurant",
    )

    search_fields = (
        "customer__phone",
        "customer__name",
    )
