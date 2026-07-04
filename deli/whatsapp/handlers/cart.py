from decimal import Decimal

from cart.services.cart_service import CartService
from whatsapp.services.navigation_service import NavigationService
from users.constants import (
    VIEW_CART,
    CHECKOUT,
    HOME,
    VIEW_ITEM,
    VIEW_MENU,
    BROWSE_RESTAURANTS,
)
from ..services.home_handler import HomeHandler
from whatsapp.services.state_service import StateService

from ..services.customer_service import CustomerService
from ..services.whatsapp_service import WhatsAppService
from .base import BaseHandler

from whatsapp.constants import NAVIGATION

class CartHandler(BaseHandler):

    def handle(self, phone, payload):

        customer, conversation, _ = (
            CustomerService.get_customer(phone)
        )

        cart = CartService.get_cart(customer)

        message = payload.strip()

        # -------------------------
        # Display Cart
        # -------------------------

        if payload.strip() == "":

            items = cart.items.select_related(
                "menu_item",
                "menu_item__restaurant",
            )

            if not items.exists():

                StateService.set(
                    conversation,
                    HOME,
                )

                WhatsAppService.send_text(
                    phone,
                    "🛒 Your cart is empty."
                )

                return HomeHandler.show(
                    phone,
                    customer,
                    conversation,
                )

            total = Decimal("0.00")

            text = "🛒 *Your Cart*\n\n"

            for index, item in enumerate(
                items,
                start=1,
            ):

                subtotal = (
                    item.menu_item.price
                    * item.quantity
                )

                total += subtotal

                text += (
                    f"{index}. {item.menu_item.name}\n"
                    f"Qty: {item.quantity}\n"
                    f"₦{subtotal}\n\n"
                )

            text += (
                f"*Total:* ₦{total}\n\n"
                "Reply:\n\n"
                "1️⃣ Checkout\n"
                "2️⃣ Continue Shopping\n"
                "3️⃣ Clear Cart"
            )

            text += NAVIGATION

            StateService.set(
                conversation,
                VIEW_CART,
                push=True,
            )

            WhatsAppService.send_text(
                phone,
                text,
            )

            return

        # -------------------------
        # VIEW CART ACTIONS
        # -------------------------

        if message == "1":

            StateService.set(
                conversation,
                CHECKOUT,
                push=True,
            )

            WhatsAppService.send_text(
                phone,
                """✅ Checkout begins in the next phase.

Payment integration is coming soon.
"""
            )

            return

        if message == "2":

            previous = NavigationService.back(
                conversation,
            )

            conversation.current_step = previous

            conversation.save(
                update_fields=[
                    "current_step",
                    "updated_at",
                ]
            )

            if previous == VIEW_MENU:
                from .menu import MenuHandler
                return MenuHandler().handle(phone, "")

            if previous == VIEW_ITEM:
                from .checkout import CheckoutHandler
                return CheckoutHandler().handle(phone, "")

            if previous == BROWSE_RESTAURANTS:
                from .restaurant import RestaurantHandler
                return RestaurantHandler().handle(phone, "")

            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

        if message == "3":

            CartService.clear_cart(customer)

            StateService.set(
                conversation,
                HOME,
            )

            WhatsAppService.send_text(
                phone,
                "🗑️ Cart cleared."
            )

            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

        WhatsAppService.send_text(
            phone,
            """Reply:

1️⃣ Checkout

2️⃣ Continue Shopping

3️⃣ Clear Cart

""" + NAVIGATION
        )