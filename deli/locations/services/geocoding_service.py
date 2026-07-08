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
    def _address_from_result(cls, result):

        address = {
            "formatted_address": result.get(
                "formatted_address",
                "",
            ),
            "state": None,
            "city": None,
            "area": None,
        }

        geometry = result.get("geometry", {})
        location = geometry.get("location", {})

        if "lat" in location:
            address["latitude"] = location["lat"]

        if "lng" in location:
            address["longitude"] = location["lng"]

        for component in result.get("address_components", []):

            types = component.get("types", [])
            long_name = component.get("long_name", "")

            if "administrative_area_level_1" in types:
                address["state"] = long_name

            elif (
                "locality" in types
                or "administrative_area_level_2" in types
            ):
                address["city"] = long_name

            elif (
                "sublocality" in types
                or "sublocality_level_1" in types
                or "neighborhood" in types
            ):
                address["area"] = long_name

        return address

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

        return cls._address_from_result(data["results"][0])

    @classmethod
    def geocode_address(cls, address):

        api_key = os.getenv(
            "GOOGLE_MAPS_API_KEY"
        )

        if not api_key:
            return {
                "formatted_address": address,
                "state": None,
                "city": None,
                "area": None,
            }

        response = requests.get(
            cls.BASE_URL,
            params={
                "address": address,
                "key": api_key,
            },
            timeout=10,
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if not data.get("results"):
            return None

        return cls._address_from_result(data["results"][0])
    
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
