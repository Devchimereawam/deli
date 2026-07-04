from users.constants import HOME
from ..services.home_handler import HomeHandler
from locations.services.location_service import LocationService

from ..services.customer_service import CustomerService
from ..services.whatsapp_service import WhatsAppService
from whatsapp.constants import NAVIGATION

from whatsapp.services.state_service import StateService

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

        StateService.set(
            conversation,
            HOME,
        )

        if customer.name:

            WhatsAppService.send_text(
                phone,
                f"""📍 Great! We've saved your delivery location.

Welcome back to Deli 🍽️ *{customer.name}* 👋

📍 Delivering to:
{customer.default_address.formatted_address}
"""
            )

            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

        StateService.set(
            conversation,
            HOME,
        )

        WhatsAppService.send_text(
            phone,
            f"""✅ Delivery location saved.
"""
        )
        return HomeHandler.show(
            phone,
            customer,
            conversation,
        )