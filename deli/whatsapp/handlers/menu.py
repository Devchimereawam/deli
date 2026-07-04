from users.constants import (
    VIEW_MENU,
)

from restaurants.services import RestaurantService
from restaurants.models import Restaurant
from ..services.customer_service import CustomerService
from ..services.whatsapp_service import WhatsAppService
from .base import BaseHandler

from whatsapp.constants import NAVIGATION
from whatsapp.services.state_service import StateService

class MenuHandler(BaseHandler):

    def handle(self, phone, payload):

        customer, conversation, _ = (
            CustomerService.get_customer(phone)
        )

        # ----------------------------
        # Restaurant Selection
        # ----------------------------

        restaurant = conversation.selected_restaurant

        if restaurant is None:

            restaurants = []

            for restaurant_id in (conversation.restaurant_ids or []):

                try:

                    restaurant = Restaurant.objects.get(
                        id=restaurant_id
                    )

                    restaurants.append(
                        restaurant
                    )

                except Restaurant.DoesNotExist:

                    continue

            try:

                index = int(payload.strip()) - 1

            except ValueError:

                WhatsAppService.send_text(
                    phone,
                    "Please reply with a restaurant number."
                )

                return

            if index < 0 or index >= len(restaurants):

                WhatsAppService.send_text(
                    phone,
                    "Restaurant not found."
                )

                return

            restaurant = restaurants[index]

            StateService.set_restaurant(
                conversation,
                restaurant,
            )

            StateService.set(
                conversation,
                VIEW_MENU,
                push=True,
            )

        else:

            restaurant = conversation.selected_restaurant

            if restaurant is None:

                WhatsAppService.send_text(
                    phone,
                    "Please reply with a restaurant number."
                )

                return

        menu = (
            restaurant.menu_items
            .filter(
                is_available=True
            )
            .select_related(
                "category"
            )
            .order_by(
                "category__name",
                "name",
            )
        )

        if not menu.exists():

            WhatsAppService.send_text(
                phone,
                "This restaurant currently has no meals available."
            )

            return

        hours = RestaurantService.format_opening_hours(
            restaurant
        )

        header = (
            f"🍽️ *{restaurant.name}*\n"
            f"⭐ {restaurant.rating} ({restaurant.total_reviews} reviews)\n"
            f"📍 {restaurant.area.name}\n"
            f"🕒 {hours}\n\n"
        )

        if restaurant.description:

            header += (
                f"{restaurant.description}\n\n"
            )

        current_category = None

        body = ""

        for index, item in enumerate(
            menu,
            start=1,
        ):

            category = (
                item.category.name
                if item.category
                else "Menu"
            )

            if category != current_category:

                current_category = category

                body += (
                    f"\n📂 *{category}*\n"
                )

            featured = (
                " ⭐"
                if item.is_featured
                else ""
            )

            image = (
                " 📷"
                if item.image
                else ""
            )

            body += (
                f"{index}. {item.name}{featured}{image}\n"
                f"₦{item.price}\n\n"
            )

        footer = (
            "Reply with the meal number to view details."
        )

        footer += NAVIGATION

        WhatsAppService.send_text(
            phone,
            header + body + footer,
        )