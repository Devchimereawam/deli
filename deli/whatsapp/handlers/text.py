from users.constants import ASK_ROLE, HOME

from orders.services.order_service import OrderService

from ..services.customer_service import CustomerService
from ..services.router_service import RouterService
from ..services.state_service import StateService


class TextHandler:

    def handle(
        self,
        phone,
        payload,
    ):

        message = payload.strip()

        if OrderService.handle_provider_reply(
            phone,
            message,
        ):
            return

        customer, conversation, created = (
            CustomerService.get_customer(phone)
        )

        ##################################################
        # FIRST TIME USER
        ##################################################

        if created:

            StateService.set(
                conversation,
                ASK_ROLE,
            )

            RouterService._prompt_role(phone)

            return

        if StateService.session_expired(conversation):
            StateService.reset(
                conversation,
                HOME,
            )

            if message.lower() in (
                "hi",
                "hello",
                "hey",
                "heu",
                "start",
                "menu",
                "home",
            ):
                return RouterService.route(
                    phone,
                    customer,
                    conversation,
                    "home",
                )

        ##################################################
        # EVERYTHING ELSE
        ##################################################

        return RouterService.route(
            phone,
            customer,
            conversation,
            message,
        )
