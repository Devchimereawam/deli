from ..services.home_handler import HomeHandler
from locations.services.location_service import LocationService

from ..services.customer_service import CustomerService

class LocationHandler:

    def handle(self, phone, payload):

        customer, conversation, created = (
            CustomerService.get_customer(phone)
        )

        if isinstance(payload, dict):

            latitude = payload["latitude"]
            longitude = payload["longitude"]

            LocationService.save_customer_location(
                customer=customer,
                latitude=latitude,
                longitude=longitude,
            )

        else:

            LocationService.save_customer_location_from_text(
                customer=customer,
                address=payload,
            )

        return HomeHandler.show(
            phone,
            customer,
            conversation,
        )
