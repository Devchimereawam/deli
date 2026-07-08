from locations.constants import DEFAULT_ADDRESS_LABEL
from locations.models import Address
from locations.utils import (
    find_city,
    resolve_location_parts,
    normalize_location_text,
)

from .geocoding_service import GeocodingService


class LocationService:

    @classmethod
    def save_customer_location(
        cls,
        customer,
        latitude,
        longitude,
    ):

        result = GeocodingService.reverse_geocode(
            latitude,
            longitude,
        )

        result = result or {}

        formatted_address = (
            result.get("formatted_address")
            or f"{latitude}, {longitude}"
        )

        return cls._save_default_address(
            customer=customer,
            latitude=latitude,
            longitude=longitude,
            formatted_address=formatted_address,
            candidates=[
                result.get("area"),
                result.get("city"),
                result.get("state"),
                formatted_address,
            ],
        )
    
    @classmethod
    def save_customer_location_from_text(
        cls,
        customer,
        address,
    ):

        typed_city = find_city(
            None,
            address,
        )

        if (
            typed_city
            and normalize_location_text(address)
            == normalize_location_text(typed_city.name)
        ):
            return cls._save_default_address(
                customer=customer,
                latitude=None,
                longitude=None,
                formatted_address=typed_city.name,
                candidates=[
                    typed_city.name,
                ],
                fallback_area_marker=False,
            )

        result = GeocodingService.geocode_address(
            address,
        )

        result = result or {
            "formatted_address": address,
        }

        return cls._save_default_address(
            customer=customer,
            latitude=result.get("latitude"),
            longitude=result.get("longitude"),
            formatted_address=result.get(
                "formatted_address",
                address,
            ),
            candidates=[
                address,
                result.get("area"),
                result.get("city"),
                result.get("state"),
                result.get("formatted_address"),
            ],
        )

    @classmethod
    def _save_default_address(
        cls,
        customer,
        formatted_address,
        candidates,
        latitude=None,
        longitude=None,
        fallback_area_marker=True,
    ):

        current = customer.default_address
        fallback_area = (
            current.area
            if fallback_area_marker and current and current.area
            else None
        )

        state, city, area = resolve_location_parts(
            *candidates,
            latitude=latitude,
            longitude=longitude,
            fallback_area=fallback_area,
        )

        Address.objects.filter(
            customer=customer,
            is_default=True,
        ).exclude(
            pk=current.pk if current else None,
        ).update(
            is_default=False,
        )

        if current:
            current.latitude = latitude
            current.longitude = longitude
            current.formatted_address = formatted_address
            current.state = state
            current.city = city
            current.area = area
            current.is_default = True
            current.save()
            return current

        return Address.objects.create(
            customer=customer,
            label=DEFAULT_ADDRESS_LABEL,
            formatted_address=formatted_address,
            latitude=latitude,
            longitude=longitude,
            state=state,
            city=city,
            area=area,
            is_default=True,
        )
