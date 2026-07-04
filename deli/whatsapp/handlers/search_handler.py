from restaurants.services.search_service import SearchService

from whatsapp.constants import NAVIGATION

from ..services.customer_service import CustomerService
from ..services.whatsapp_service import WhatsAppService
from .base import BaseHandler
from whatsapp.services.state_service import StateService

from .menu import MenuHandler
from restaurants.models import Restaurant
from .checkout import CheckoutHandler

from users.constants import VIEW_MENU, VIEW_ITEM

class SearchHandler(BaseHandler):

    def handle(self, phone, payload):

        customer, conversation, _ = (
            CustomerService.get_customer(phone)
        )
        
        if payload.strip().isdigit():

            ids = conversation.search_result_ids

            index = int(payload) - 1

            if index < 0 or index >= len(ids):

                WhatsAppService.send_text(
                    phone,
                    "Invalid selection."
                )

                return

            result_type = conversation.search_result_type[index]

            if result_type == "restaurant":

                restaurant = Restaurant.objects.get(
                    id=ids[index],
                )

                StateService.set_restaurant(
                    conversation,
                    restaurant,
                )

                StateService.go_to(
                    conversation,
                    VIEW_MENU,
                )

                return MenuHandler().handle(
                    phone,
                    "",
                )

            elif result_type == "food":

                from restaurants.models import MenuItem
                from restaurants.services import RestaurantService
                from whatsapp.handlers.checkout import BASE_URL

                item = MenuItem.objects.get(
                    id=ids[index],
                )

                StateService.set_restaurant(
                    conversation,
                    item.restaurant,
                )

                StateService.set_menu_item(
                    conversation,
                    item,
                )

                StateService.go_to(
                    conversation,
                    VIEW_ITEM,
                )

                restaurant = item.restaurant

                hours = RestaurantService.format_opening_hours(
                    restaurant,
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

            """
                    + NAVIGATION
                )

                return

        query = payload.strip()

        restaurants, foods = SearchService.search(
            customer,
            query,
        )

        text = ""

        ids = []
        types = []

        if restaurants.exists():

            text += "🍽️ *RESTAURANTS*\n\n"

            for restaurant in restaurants[:10]:

                ids.append(restaurant.id)
                types.append("restaurant")

                text += (
                    f"{len(ids)}. {restaurant.name}\n"
                    f"⭐ {restaurant.rating}\n\n"
                )

        if foods.exists():

            text += "\n━━━━━━━━━━━━━━\n\n"

            text += "🍔 *FOOD*\n\n"

            for food in foods[:10]:

                ids.append(food.id)
                types.append("food")

                text += (
                    f"{len(ids)}. {food.name}\n"
                    f"🏪 {food.restaurant.name}\n"
                    f"💰 ₦{food.price}\n\n"
                )

        if not ids:

            WhatsAppService.send_text(
                phone,
                "😔 Nothing found."
            )

            return

        conversation.search_result_ids = ids
        conversation.search_result_type = types

        conversation.save(
            update_fields=[
                "search_result_ids",
                "search_result_type",
            ]
        )

        WhatsAppService.send_text(
            phone,
            text + NAVIGATION,
        )