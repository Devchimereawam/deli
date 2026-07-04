import os

BASE_URL = os.getenv(
    "NGROK_URL",
    "",
).rstrip("/")
from cart.services.cart_service import CartService

from users.constants import (
    VIEW_ITEM,
    VIEW_CART,
    VIEW_MENU,
)

from restaurants.services import RestaurantService

from ..services.customer_service import CustomerService
from ..services.whatsapp_service import WhatsAppService
from .base import BaseHandler

from whatsapp.constants import NAVIGATION

from whatsapp.services.state_service import StateService

class CheckoutHandler(BaseHandler):

    def handle(self, phone, payload):

        customer, conversation, _ = (
            CustomerService.get_customer(phone)
        )

        # -----------------------------------
        # Selecting meal from menu
        # -----------------------------------

        if (
            conversation.current_step != VIEW_ITEM
            and conversation.selected_menu_item is None
        ):

            restaurant = conversation.selected_restaurant

            if restaurant is None:

                WhatsAppService.send_text(
                    phone,
                    "Please choose a restaurant first."
                )

                return

            menu = list(
                restaurant.menu_items.filter(
                    is_available=True,
                )
                .select_related(
                    "category",
                )
                .order_by(
                    "category__name",
                    "name",
                )
            )

            try:

                index = int(payload.strip()) - 1

            except ValueError:

                WhatsAppService.send_text(
                    phone,
                    "Please reply with a valid meal number."
                )

                return

            if index < 0 or index >= len(menu):

                WhatsAppService.send_text(
                    phone,
                    "Meal not found."
                )

                return

            item = menu[index]
            
            conversation.selected_menu_item = item
            conversation.save(
                update_fields=[
                    "selected_menu_item",
                ]
            )

            StateService.set_menu_item(
                conversation,
                item,
            )

            StateService.set(
                conversation,
                VIEW_ITEM,
                push=True,
            )

            hours = RestaurantService.format_opening_hours(
                restaurant
            )

            description = (
                item.description
                if item.description
                else "No description available."
            )

            if item.image:

                WhatsAppService.send_image(
                    phone,
                    f"{BASE_URL}{item.image.url}",
                    item.name,
                )

            WhatsAppService.send_text(
                phone,
                f"""🍽️ *{item.name}*

🏪 {restaurant.name}

💰 ₦{item.price}

📝 {description}

⭐ Rating: {restaurant.rating}

🕒 {hours}

Reply:

1️⃣ Add to Cart

2️⃣ Back to Menu

""" + NAVIGATION
            )

            return

        # -----------------------------------
        # VIEW ITEM
        # -----------------------------------

        if payload.strip() == "1":

            CartService.add_item(
                customer,
                conversation.selected_menu_item,
            )

            StateService.set(
                conversation,
                VIEW_CART,
                push=True,
            )

            from .cart import CartHandler

            return CartHandler().handle(
                phone,
                "",
            )

        if payload.strip() == "2":

            StateService.clear_selection(
                conversation,
            )

            StateService.set(
                conversation,
                VIEW_MENU,
            )

            from .menu import MenuHandler

            return MenuHandler().handle(
                phone,
                ""
            )

        WhatsAppService.send_text(
            phone,
            """Reply:

1️⃣ Add to Cart

2️⃣ Back to Menu

""" + NAVIGATION
        )