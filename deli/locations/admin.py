from django.contrib import admin

from .models import (
    Address,
    Area,
    City,
    State,
)


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "state",
    )

    list_filter = (
        "state",
    )

    search_fields = (
        "name",
    )


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "city",
        "latitude",
        "longitude",
    )

    list_filter = (
        "city",
    )

    search_fields = (
        "name",
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "customer",
        "label",
        "area",
        "city",
        "state",
        "is_default",
    )

    list_filter = (
        "state",
        "city",
        "is_default",
    )

    search_fields = (
        "customer__phone",
        "customer__name",
        "formatted_address",
    )