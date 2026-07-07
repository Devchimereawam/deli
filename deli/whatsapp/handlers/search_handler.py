from restaurants.services.search_service import SearchService

from whatsapp.constants import NAVIGATION
from whatsapp.services.formatting import money

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

                return CheckoutHandler.send_meal_detail(
                    phone,
                    item.restaurant,
                    item,
                )

        query = payload.strip()

        restaurants, foods = SearchService.search(
            customer,
            query,
        )

        text = ""

        ids = []
        types = []

        rows = []

        if restaurants.exists():

            text += "🍽️ *Restaurants*\n\n"

            for restaurant in restaurants[:10]:

                ids.append(restaurant.id)
                types.append("restaurant")

                text += (
                    f"{len(ids)}. *{restaurant.name}*\n"
                    f"   ⭐ {restaurant.rating} ({restaurant.total_reviews})\n"
                    f"   📍 {restaurant.area.name}\n\n"
                )
                rows.append(
                    (
                        str(len(ids)),
                        restaurant.name,
                        f"Restaurant · ⭐ {restaurant.rating}",
                    )
                )

        if foods.exists():

            text += "\n━━━━━━━━━━━━━━\n\n"

            text += "🍔 *Meals*\n\n"

            for food in foods[:10]:

                ids.append(food.id)
                types.append("food")

                text += (
                    f"{len(ids)}. *{food.name}*\n"
                    f"   🏪 {food.restaurant.name}\n"
                    f"   💰 {money(food.price)}\n"
                    f"   ⭐ {food.rating} ({food.total_reviews})\n\n"
                )
                rows.append(
                    (
                        str(len(ids)),
                        food.name,
                        f"{money(food.price)} · {food.restaurant.name}",
                    )
                )

        if not ids:

            WhatsAppService.send_text(
                phone,
                "😔 Nothing found in your area. Try a different food name or change location."
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

        WhatsAppService.send_list(
            phone,
            text + NAVIGATION,
            rows,
            "Choose item",
            "You can also reply with the number.",
        )
