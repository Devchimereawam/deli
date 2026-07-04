import os
from users.constants import (
    BROWSE_RESTAURANTS,
)
from restaurants.services import RestaurantService

from ..services.customer_service import CustomerService
from ..services.whatsapp_service import WhatsAppService
from .base import BaseHandler
from whatsapp.services.state_service import StateService

from whatsapp.constants import NAVIGATION

BASE_URL = os.getenv("NGROK_URL", "").rstrip("/")

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
            [r.id for r in restaurants],
        )

        if not restaurants:

            WhatsAppService.send_text(
                phone,
                """😔 We couldn't find any restaurants delivering to your area.

Try changing your location or check back later."""
            )
            return

        StateService.set(
            conversation,
            BROWSE_RESTAURANTS,
            push=True,
        )

        message = (
            "🍽️ *Restaurants Near You*\n\n"
        )

        for index, restaurant in enumerate(
            restaurants,
            start=1,
        ):

            hours = RestaurantService.format_opening_hours(
                restaurant,
            )

            caption = (
                f"{index}. *{restaurant.name}*\n"
                f"⭐ {restaurant.rating} ({restaurant.total_reviews})\n"
                f"📍 {restaurant.area.name}\n"
                f"🕒 {hours}\n\n"
                f"{restaurant.description or ''}"
            )

            if restaurant.cover_image:

                WhatsAppService.send_image(
                    phone,
                    f"{BASE_URL}{restaurant.cover_image.url}",
                    caption,
                )

            else:

                WhatsAppService.send_text(
                    phone,
                    caption,
                )

        WhatsAppService.send_text(
            phone,
            "Reply with the restaurant number."
            + NAVIGATION,
        )

"""         for restaurant in restaurants:

            caption = (
                f"🍽️ *{restaurant.name}*\n"
                f"⭐ {restaurant.rating}\n"
                f"📍 {restaurant.area.name}\n\n"
                f"{restaurant.description}"
            )

            if restaurant.cover_image_url:

                WhatsAppService.send_image(
                    phone,
                    f"{BASE_URL}{restaurant.cover_image.url}",
                    caption,
                )

            else:

                WhatsAppService.send_text(
                    phone,
                    caption,
                )

        WhatsAppService.send_text(
            phone,
            "Reply with the restaurant number."
        ) """