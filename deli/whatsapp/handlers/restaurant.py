from users.constants import BROWSE_RESTAURANTS

from restaurants.services import RestaurantService

from ..services.customer_service import CustomerService
from ..services.whatsapp_service import WhatsAppService
from .base import BaseHandler
from whatsapp.constants import NAVIGATION
from whatsapp.services.state_service import StateService


class RestaurantHandler(BaseHandler):

    def handle(self, phone, payload):

        customer, conversation, _ = (
            CustomerService.get_customer(phone)
        )

        restaurants = list(
            RestaurantService.nearby_restaurants(
                customer
            )
        )

        StateService.set_restaurant_list(
            conversation,
            [restaurant.id for restaurant in restaurants],
        )

        if not restaurants:
            WhatsAppService.send_text(
                phone,
                """😔 We couldn't find any restaurants delivering to your area.

Try changing your location or check back later."""
                + NAVIGATION,
            )
            return

        StateService.set(
            conversation,
            BROWSE_RESTAURANTS,
            push=True,
        )

        text = "🍽️ *Restaurants Near You*\n\nChoose a number to open a restaurant menu.\n\n"

        best = restaurants[:3]

        if best:
            text += "⭐ *Best Rated Restaurants*\n"

            for index, restaurant in enumerate(
                best,
                start=1,
            ):
                text += (
                    f"{index}. *{restaurant.name}*\n"
                    f"   ⭐ ({restaurant.rating}) ({restaurant.total_reviews})\n"
                )

            text += "\n────────────\n\n*All Available Restaurants*\n"

        rows = []

        for index, restaurant in enumerate(
            restaurants,
            start=1,
        ):
            hours = RestaurantService.format_opening_hours(
                restaurant,
            )

            text += (
                f"{index}. *{restaurant.name}*\n"
                f"   ⭐ {restaurant.rating} ({restaurant.total_reviews})\n"
                f"   📍 {restaurant.area.name}\n"
                f"   🕒 {hours}\n"
            )

            if restaurant.description:
                text += f"{restaurant.description}\n"

            text += "\n"
            rows.append(
                (
                    str(index),
                    restaurant.name,
                    f"⭐ {restaurant.rating} · {restaurant.area.name}",
                )
            )

        text += "Reply with the restaurant number to view its logo and menu."
        text += NAVIGATION

        WhatsAppService.send_list(
            phone,
            text,
            rows,
            "Choose restaurant",
            "You can also reply with the number.",
        )
