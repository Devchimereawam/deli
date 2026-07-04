from users.constants import ASK_LOCATION

from ..services.customer_service import CustomerService
from ..services.router_service import RouterService
from ..services.state_service import StateService
from ..services.whatsapp_service import WhatsAppService


class TextHandler:

    def handle(
        self,
        phone,
        payload,
    ):

        message = payload.strip()

        customer, conversation, created = (
            CustomerService.get_customer(phone)
        )

        ##################################################
        # FIRST TIME USER
        ##################################################

        if created:

            StateService.set(
                conversation,
                ASK_LOCATION,
            )

            WhatsAppService.send_text(
                phone,
                """👋 Welcome to Deli!

This looks like your first time here.

Let's get you set up.

📍 Please share your location.

If location sharing doesn't work, simply type your delivery area."""
            )

            WhatsAppService.request_location(
                phone,
            )

            return

        ##################################################
        # EVERYTHING ELSE
        ##################################################

        return RouterService.route(
            phone,
            customer,
            conversation,
            message,
        )