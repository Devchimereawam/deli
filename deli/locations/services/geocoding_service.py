import os

import requests


class GeocodingService:
    """
    Reverse geocoding service.

    Uses Google Maps Geocoding API.
    """

    BASE_URL = (
        "https://maps.googleapis.com/maps/api/geocode/json"
    )

    @classmethod
    def reverse_geocode(cls, latitude, longitude):

        api_key = os.getenv(
            "GOOGLE_MAPS_API_KEY"
        )

        if not api_key:
            return None

        response = requests.get(
            cls.BASE_URL,
            params={
                "latlng": f"{latitude},{longitude}",
                "key": api_key,
            },
            timeout=10,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if not data.get("results"):
            return None

        result = data["results"][0]

        address = {
            "formatted_address": result.get(
                "formatted_address",
                "",
            ),
            "state": None,
            "city": None,
            "area": None,
        }

        for component in result["address_components"]:

            types = component["types"]

            if "administrative_area_level_1" in types:
                address["state"] = component["long_name"]

            elif (
                "locality" in types
                or "administrative_area_level_2" in types
            ):
                address["city"] = component["long_name"]

            elif (
                "sublocality" in types
                or "neighborhood" in types
            ):
                address["area"] = component["long_name"]

        return address
    
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
            return None

        return cls.save_customer_location(
            customer=customer,
            latitude=result["latitude"],
            longitude=result["longitude"],
        )