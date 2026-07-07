import os

from users.constants import VIEW_MENU

from restaurants.models import Restaurant
from restaurants.services import RestaurantService
from ..services.customer_service import CustomerService
from ..services.whatsapp_service import WhatsAppService
from .base import BaseHandler
from whatsapp.constants import NAVIGATION
from whatsapp.services.formatting import money
from whatsapp.services.state_service import StateService

BASE_URL = (
    os.getenv("PUBLIC_BASE_URL")
    or os.getenv("NGROK_URL", "")
).rstrip("/")


class MenuHandler(BaseHandler):

    def handle(self, phone, payload):

        customer, conversation, _ = (
            CustomerService.get_customer(phone)
        )

        restaurant = conversation.selected_restaurant

        if restaurant is None:
            restaurant = self._select_restaurant(
                phone,
                conversation,
                payload,
            )

            if restaurant is None:
                return

            StateService.set_restaurant(
                conversation,
                restaurant,
            )

            StateService.set(
                conversation,
                VIEW_MENU,
                push=True,
            )

        return self._show_menu(
            phone,
            restaurant,
        )

    def _select_restaurant(
        self,
        phone,
        conversation,
        payload,
    ):

        restaurants = []

        for restaurant_id in (conversation.restaurant_ids or []):
            try:
                restaurants.append(
                    Restaurant.objects.get(
                        id=restaurant_id,
                        is_active=True,
                    )
                )
            except Restaurant.DoesNotExist:
                continue

        try:
            index = int(payload.strip()) - 1
        except ValueError:
            WhatsAppService.send_text(
                phone,
                "Please reply with a restaurant number."
                + NAVIGATION,
            )
            return None

        if index < 0 or index >= len(restaurants):
            WhatsAppService.send_text(
                phone,
                "Restaurant not found. Please choose a number from the restaurant list."
                + NAVIGATION,
            )
            return None

        return restaurants[index]

    def _show_menu(
        self,
        phone,
        restaurant,
    ):

        menu = (
            restaurant.menu_items
            .select_related(
                "category",
                "inventory",
            )
            .order_by(
                "category__name",
                "name",
            )
        )

        menu_items = list(menu)

        if not menu_items:
            WhatsAppService.send_text(
                phone,
                "This restaurant currently has no meals listed."
                + NAVIGATION,
            )
            return

        hours = RestaurantService.format_opening_hours(
            restaurant
        )

        text = (
            f"🍽️ *{restaurant.name}*\n"
            f"⭐ {restaurant.rating} ({restaurant.total_reviews} reviews)\n"
            f"📍 {restaurant.area.name}\n"
            f"🕒 {hours}\n"
            f"⏱️ Prep: {restaurant.estimated_prep_minutes} mins\n\n"
        )

        if restaurant.description:
            text += f"{restaurant.description}\n\n"

        current_category = None
        rows = []

        for index, item in enumerate(
            menu_items,
            start=1,
        ):
            category = (
                item.category.name
                if item.category
                else "Menu"
            )

            if category != current_category:
                current_category = category
                text += f"\n📂 *{category}*\n"

            featured = " ⭐" if item.is_featured else ""
            image = " 📷" if item.image else ""
            status = (
                "Available"
                if self._is_item_available(item)
                else "Unavailable"
            )
            stock = self._stock_text(item)

            text += (
                f"{index}. *{item.name}*{featured}{image}\n"
                f"   {money(item.price)}\n"
                f"   {status} · {stock}\n\n"
            )
            rows.append(
                (
                    str(index),
                    item.name,
                    f"{money(item.price)} · {status}",
                )
            )

        text += "Choose a meal to view its photo, rating, and add-to-cart option."
        text += NAVIGATION

        WhatsAppService.send_list(
            phone,
            text,
            rows,
            "Choose meal",
            "You can also reply with the meal number.",
        )

    @staticmethod
    def _is_item_available(item):

        if not item.is_available:
            return False

        if hasattr(item, "inventory"):
            return item.inventory.quantity > 0

        return True

    @staticmethod
    def _stock_text(item):

        if hasattr(item, "inventory"):
            return f"Stock: {item.inventory.quantity}"

        return "Stock: Available"
