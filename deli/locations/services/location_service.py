from locations.constants import DEFAULT_ADDRESS_LABEL
from locations.models import Address, Area
from locations.utils import (
    find_area,
    find_city,
    find_state,
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

        if not result:

            address = customer.default_address

            if address:

                address.latitude = latitude
                address.longitude = longitude
                address.save()

                return address

            return Address.objects.create(
                customer=customer,
                label=DEFAULT_ADDRESS_LABEL,
                latitude=latitude,
                longitude=longitude,
                is_default=True,
            )

        state = find_state(
            result.get("state"),
        )

        city = find_city(
            state,
            result.get("city"),
        )

        area = find_area(
            city,
            result.get("area"),
        )

        address = customer.default_address

        if address:

            Address.objects.filter(
                customer=customer,
                is_default=True,
            ).exclude(
                pk=address.pk,
            ).update(
                is_default=False,
            )

        if address:

            address.latitude = latitude
            address.longitude = longitude
            address.formatted_address = result.get(
                "formatted_address",
                "",
            )
            address.state = state
            address.city = city
            address.area = area
            address.is_default = True

            address.save()

            return address

        return Address.objects.create(
            customer=customer,
            label=DEFAULT_ADDRESS_LABEL,
            latitude=latitude,
            longitude=longitude,
            formatted_address=result.get(
                "formatted_address",
                "",
            ),
            state=state,
            city=city,
            area=area,
            is_default=True,
        )
    
    @classmethod
    def save_customer_location_from_text(
        cls,
        customer,
        address,
    ):

        result = GeocodingService.geocode_address(
            address,
        )

        if not result:
            current = customer.default_address
            fallback_area = (
                current.area
                if current and current.area
                else Area.objects.first()
            )
            fallback_city = fallback_area.city if fallback_area else None
            fallback_state = (
                fallback_city.state
                if fallback_city
                else None
            )

            if current:
                current.formatted_address = address
                current.area = fallback_area
                current.city = fallback_city
                current.state = fallback_state
                current.is_default = True
                current.save()
                return current

            return Address.objects.create(
                customer=customer,
                label=DEFAULT_ADDRESS_LABEL,
                formatted_address=address,
                area=fallback_area,
                city=fallback_city,
                state=fallback_state,
                is_default=True,
            )

        return cls.save_customer_location(
            customer=customer,
            latitude=result["latitude"],
            longitude=result["longitude"],
        )
