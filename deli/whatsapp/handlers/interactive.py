from .base import BaseHandler
from ..services.customer_service import CustomerService
from ..services.router_service import RouterService


class InteractiveHandler(BaseHandler):

    def handle(self, phone, payload):

        message = self._extract_reply(payload)

        if not message:
            return

        customer, conversation, _ = CustomerService.get_customer(phone)

        return RouterService.route(
            phone,
            customer,
            conversation,
            message,
        )

    @staticmethod
    def _extract_reply(payload):

        interactive = payload.get("interactive", {})

        if "button_reply" in interactive:
            reply = interactive["button_reply"]
            return reply.get("id") or reply.get("title")

        if "list_reply" in interactive:
            reply = interactive["list_reply"]
            return reply.get("id") or reply.get("title")

        button = payload.get("button", {})

        return (
            button.get("payload")
            or button.get("text")
            or ""
        )
