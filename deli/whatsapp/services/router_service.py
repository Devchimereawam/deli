from users.constants import (
    HOME,
    ASK_LOCATION,
    ASK_NAME,
    SEARCH_RESTAURANTS,
    BROWSE_RESTAURANTS,
    VIEW_MENU,
    VIEW_ITEM,
    VIEW_CART,
    CHECKOUT,
    ORDER_STATUS,
)

from cart.services.cart_service import CartService

from .state_service import StateService
from .navigation_service import NavigationService
from .home_handler import HomeHandler

from whatsapp.handlers.location import LocationHandler
from whatsapp.handlers.restaurant import RestaurantHandler
from whatsapp.handlers.menu import MenuHandler
from whatsapp.handlers.checkout import CheckoutHandler
from whatsapp.handlers.cart import CartHandler
from whatsapp.handlers.search_handler import SearchHandler

from ..services.customer_service import CustomerService
from ..services.whatsapp_service import WhatsAppService


class RouterService:

    @classmethod
    def route(
        cls,
        phone,
        customer,
        conversation,
        message,
    ):

        command = message.lower().strip()

        ##################################################
        # GLOBAL COMMANDS
        ##################################################

        if command in ("0", "home", "menu"):

            StateService.reset(
                conversation,
                HOME,
            )

            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

        ##################################################

        if command in (
            "8",
            "cart",
            "view cart",
        ):

            StateService.set(
                conversation,
                VIEW_CART,
                push=True,
            )

            return CartHandler().handle(
                phone,
                "",
            )

        ##################################################

        if command == "clear cart":

            CartService.clear_cart(customer)

            StateService.reset(
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

        ##################################################

        if command.startswith("search "):

            query = command.replace(
                "search",
                "",
                1,
            ).strip()

            StateService.set(
                conversation,
                SEARCH_RESTAURANTS,
                push=True,
            )

            StateService.set_search(
                conversation,
                query,
            )

            return SearchHandler().handle(
                phone,
                query,
            )

        ##################################################

        if command in ("9", "back"):

            previous = NavigationService.back(
                conversation,
            )

            StateService.go_to(
                conversation,
                previous,
            )

            state = previous

        else:

            state = StateService.get(
                conversation,
            )

        ##################################################
        # SCREEN ROUTING
        ##################################################

        if state == ASK_LOCATION:

            return LocationHandler().handle(
                phone,
                message,
            )

        ##################################################

        if state == ASK_NAME:

            CustomerService.save_name(
                customer,
                message,
            )

            StateService.reset(
                conversation,
                HOME,
            )

            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

        ##################################################

        if state == HOME:

            if command in (
                "1",
                "browse",
                "browse restaurants",
                "restaurant",
                "restaurants",
            ):

                return RestaurantHandler().handle(
                    phone,
                    message,
                )

            if command in (
                "2",
                "search",
                "search food",
                "food",
            ):

                StateService.set(
                    conversation,
                    SEARCH_RESTAURANTS,
                    push=True,
                )

                WhatsAppService.send_text(
                    phone,
                    """🔎 Search Food

        Type the food or restaurant name.
        """
                )

                return

            if message == "3":

                StateService.set(
                    conversation,
                    ORDER_STATUS,
                )

                WhatsAppService.send_text(
                    phone,
                    """📦 My Orders

            You don't have any orders yet.

            Once you've placed an order, you'll be able to track it here.

            Reply with:

            1️⃣ Browse Restaurants

            0️⃣ Home
            """
                )

                return

            if command in (
                "4",
                "location",
                "change location",
                "change address",
            ):

                StateService.set(
                    conversation,
                    ASK_LOCATION,
                    push=True,
                )

                WhatsAppService.request_location(
                    phone,
                )
                
                return

            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

        ##################################################

        if state == SEARCH_RESTAURANTS:

            return SearchHandler().handle(
                phone,
                message,
            )

        ##################################################

        if state == BROWSE_RESTAURANTS:

            return MenuHandler().handle(
                phone,
                message,
            )

        ##################################################

        if state == VIEW_MENU:

            if conversation.selected_menu_item:

                return CheckoutHandler().handle(
                    phone,
                    message,
                )

            return MenuHandler().handle(
                phone,
                message,
            )

        ##################################################

        if state == VIEW_ITEM:

            return CheckoutHandler().handle(
                phone,
                message,
            )

        ##################################################

        if state == VIEW_CART:

            return CartHandler().handle(
                phone,
                message,
            )

        ##################################################

        if state == CHECKOUT:

            return CartHandler().handle(
                phone,
                message,
            )

        ##################################################

        StateService.reset(
            conversation,
            HOME,
        )

        return HomeHandler.show(
            phone,
            customer,
            conversation,
        )