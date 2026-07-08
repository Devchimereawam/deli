import os

import requests

from cart.services.cart_service import CartService
from delivery.models import DeliveryRider
from delivery.services import DeliveryService
from orders.models import Order
from orders.services.order_service import OrderService
from payments.services.payment_service import PaymentService

from users.constants import (
    CHECKOUT,
    CHECKOUT_ASK_NAME,
    CONFIRM_DELIVERY_DETAILS,
    PAYMENT,
    SELECT_DELIVERY_RIDER,
    VIEW_CART,
    VIEW_ITEM,
    VIEW_MENU,
)

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


class CheckoutHandler(BaseHandler):

    def handle(self, phone, payload):

        customer, conversation, _ = CustomerService.get_customer(phone)
        message = payload.strip()

        if conversation.current_step == CHECKOUT:
            return self._handle_delivery_details(
                phone,
                customer,
                conversation,
                message,
            )

        if conversation.current_step == CONFIRM_DELIVERY_DETAILS:
            return self._handle_delivery_confirmation(
                phone,
                customer,
                conversation,
                message,
            )

        if conversation.current_step == SELECT_DELIVERY_RIDER:
            return self._handle_rider_selection(
                phone,
                customer,
                conversation,
                message,
            )

        if (
            conversation.current_step != VIEW_ITEM
            and conversation.selected_menu_item is None
        ):
            return self._select_meal(
                phone,
                conversation,
                message,
            )

        if message == "1":
            if conversation.selected_menu_item is None:
                WhatsAppService.send_text(
                    phone,
                    "That meal selection expired. Please choose a meal again."
                    + NAVIGATION,
                )
                StateService.set(
                    conversation,
                    VIEW_MENU,
                )
                from .menu import MenuHandler
                return MenuHandler().handle(phone, "")

            if not self._is_item_available(conversation.selected_menu_item):
                WhatsAppService.send_text(
                    phone,
                    "This meal is currently unavailable."
                    + NAVIGATION,
                )
                return

            try:
                CartService.add_item(
                    customer,
                    conversation.selected_menu_item,
                )
            except ValueError as exc:
                WhatsAppService.send_text(
                    phone,
                    f"{exc}\n\nType clear cart to start a new order."
                    + NAVIGATION,
                )
                return

            conversation.selected_menu_item = None
            conversation.save(
                update_fields=[
                    "selected_menu_item",
                    "updated_at",
                ]
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

        if message in (
            "2",
            "3",
            "back",
            "menu",
            "back to menu",
        ):
            conversation.selected_menu_item = None
            conversation.save(
                update_fields=[
                    "selected_menu_item",
                    "updated_at",
                ]
            )

            StateService.set(
                conversation,
                VIEW_MENU,
            )

            from .menu import MenuHandler

            return MenuHandler().handle(
                phone,
                "",
            )

        WhatsAppService.send_text(
            phone,
            """Reply:

1️⃣ Add to Cart

2️⃣ Back to Menu

3️⃣ Menu

"""
            + NAVIGATION,
        )

    def _select_meal(
        self,
        phone,
        conversation,
        message,
    ):

        restaurant = conversation.selected_restaurant

        if restaurant is None:
            WhatsAppService.send_text(
                phone,
                "Please choose a restaurant first."
                + NAVIGATION,
            )
            return

        menu = list(
            restaurant.menu_items.all()
            .select_related(
                "category",
                "inventory",
            )
            .order_by(
                "category__name",
                "name",
            )
        )

        try:
            index = int(message) - 1
        except ValueError:
            WhatsAppService.send_text(
                phone,
                "Please reply with a valid meal number."
                + NAVIGATION,
            )
            return

        if index < 0 or index >= len(menu):
            WhatsAppService.send_text(
                phone,
                "Meal not found. Please choose a number from this menu."
                + NAVIGATION,
            )
            return

        item = menu[index]
        StateService.set_menu_item(
            conversation,
            item,
        )

        StateService.set(
            conversation,
            VIEW_ITEM,
            push=True,
        )

        return self.send_meal_detail(
            phone,
            restaurant,
            item,
        )

    @classmethod
    def send_meal_detail(
        cls,
        phone,
        restaurant,
        item,
    ):

        description = (
            item.description
            if item.description
            else "No description available."
        )

        available = cls._is_item_available(item)
        stock_text = cls._stock_text(item)
        buttons = [
            ("2", "Back to Menu"),
            ("3", "Menu"),
        ]

        if available:
            buttons.insert(
                0,
                ("1", "Add to Cart"),
            )

        detail = f"""🍽️ *{item.name}*

🏪 {restaurant.name}

💰 {money(item.price)}

📝 {description}

⭐ Meal Rating: {item.rating} ({item.total_reviews})

Status: {'Available' if available else 'Unavailable'}
{stock_text}

"""
        detail += NAVIGATION

        if item.image:
            WhatsAppService.send_image_buttons(
                phone,
                item.image,
                detail,
                buttons,
                "You can also reply 1, 2, or 3.",
            )
        else:
            WhatsAppService.send_buttons(
                phone,
                detail,
                buttons,
                "You can also reply 1, 2, or 3.",
            )

    def start_checkout(
        self,
        phone,
        conversation,
    ):

        if not conversation.customer.name:
            StateService.set(
                conversation,
                CHECKOUT_ASK_NAME,
                push=True,
            )
            WhatsAppService.send_text(
                phone,
                "Before checkout, what is your name?",
            )
            return

        StateService.set(
            conversation,
            CHECKOUT,
            push=True,
        )

        WhatsAppService.send_text(
            phone,
            """📍 *Delivery Details*

Send your delivery details in one message:

Address: Your exact delivery address

Phone: Phone number the rider can call

Notes: Nearest landmark or delivery instruction

Example:
Address: 12 Admiralty Way, Lekki Phase 1
Phone: 08012345678
Notes: Call when outside"""
            + NAVIGATION,
        )

    def _handle_delivery_details(
        self,
        phone,
        customer,
        conversation,
        message,
    ):

        if not message:
            return self.start_checkout(
                phone,
                conversation,
            )

        details = self._parse_delivery_details(
            message,
            customer,
        )

        if not details["address"]:
            WhatsAppService.send_text(
                phone,
                "Please include your exact delivery address."
                + NAVIGATION,
            )
            return

        StateService.set_delivery_details(
            conversation,
            details["address"],
            details["phone"],
            details["notes"],
        )

        StateService.set(
            conversation,
            CONFIRM_DELIVERY_DETAILS,
            push=True,
        )

        WhatsAppService.send_buttons(
            phone,
            f"""Please confirm these delivery details:

Address:
{details["address"]}

Phone:
{details["phone"]}

Notes:
{details["notes"] or "None"}

Keep your phone reachable and nearby.""",
            [
                ("1", "Continue"),
                ("back", "Go Back"),
            ],
            "You can also reply 1 to continue or back.",
        )

    def _handle_delivery_confirmation(
        self,
        phone,
        customer,
        conversation,
        message,
    ):

        if message == "1":
            StateService.set(
                conversation,
                SELECT_DELIVERY_RIDER,
                push=True,
            )
            return self._show_riders(
                phone,
                customer,
            )

        if message in ("2", "back"):
            return self.start_checkout(
                phone,
                conversation,
            )

        WhatsAppService.send_text(
            phone,
            "Reply 1 to continue or back to edit delivery details."
            + NAVIGATION,
        )

    def _parse_delivery_details(
        self,
        message,
        customer,
    ):

        details = {
            "address": "",
            "phone": customer.phone,
            "notes": "",
        }

        current = None
        free_lines = []

        for raw_line in message.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            lower = line.lower()

            if lower.startswith("address:"):
                current = "address"
                details[current] = line.split(":", 1)[1].strip()
                continue

            if lower.startswith("phone:"):
                current = "phone"
                details[current] = line.split(":", 1)[1].strip()
                continue

            if lower.startswith("notes:"):
                current = "notes"
                details[current] = line.split(":", 1)[1].strip()
                continue

            if current:
                details[current] = (
                    f"{details[current]}\n{line}".strip()
                )
            else:
                free_lines.append(line)

        if not details["address"] and free_lines:
            details["address"] = "\n".join(free_lines)

        return details

    def _show_riders(
        self,
        phone,
        customer,
    ):

        options = DeliveryService.rider_options(
            customer,
        )

        text = "🏍️ *Choose Delivery*\n\n"
        rows = []

        for index, option in enumerate(
            options,
            start=1,
        ):
            text += (
                "────────────\n"
                f"{index}. *{option['name']}*\n"
                f"Fee: {money(option['fee'])}\n"
                f"⭐ {option['rating']} ({option['reviews']} reviews)\n"
                f"{option['vehicle']}\n\n"
            )
            rows.append(
                (
                    str(index),
                    option["name"],
                    f"{money(option['fee'])} · ⭐ {option['rating']} · {option['vehicle']}",
                )
            )

        text += "Reply with the delivery option number."
        text += NAVIGATION

        WhatsAppService.send_list(
            phone,
            text,
            rows,
            "Choose rider",
            "You can also reply with the number.",
        )

    def _handle_rider_selection(
        self,
        phone,
        customer,
        conversation,
        message,
    ):

        options = DeliveryService.rider_options(
            customer,
        )

        try:
            index = int(message) - 1
        except ValueError:
            WhatsAppService.send_text(
                phone,
                "Please reply with a delivery option number."
                + NAVIGATION,
            )
            return

        if index < 0 or index >= len(options):
            WhatsAppService.send_text(
                phone,
                "Delivery option not found."
                + NAVIGATION,
            )
            return

        existing_order = conversation.selected_order

        if (
            existing_order
            and existing_order.status == Order.STATUS_AWAITING_PAYMENT
            and existing_order.checkout_url
        ):
            StateService.set(
                conversation,
                PAYMENT,
                push=True,
            )
            WhatsAppService.send_url_button(
                phone,
                f"""💳 *Payment already started*

Order: *{existing_order.checkout_reference}*
Total: {money(existing_order.total)}

We use Nomba for secure payments. Tap Continue to pay in your browser.

After payment, Deli will confirm the restaurant and delivery rider.""",
                "Continue",
                existing_order.checkout_url,
                fallback_text=f"""💳 *Payment already started*

Order: *{existing_order.checkout_reference}*
Total: {money(existing_order.total)}

Pay securely with Nomba:
{existing_order.checkout_url}""",
            )
            return

        option = options[index]
        rider = None

        if option["kind"] == "rider":
            rider = DeliveryRider.objects.get(
                id=option["id"],
            )

        StateService.set_delivery_rider(
            conversation,
            rider,
        )

        try:
            order = OrderService.create_order(
                customer,
                delivery_address=conversation.delivery_address,
                delivery_contact_phone=conversation.delivery_contact_phone,
                delivery_notes=conversation.delivery_notes,
                delivery_rider=rider,
                delivery_fee=option["fee"],
            )

            if order is None:
                WhatsAppService.send_text(
                    phone,
                    "Your cart is empty."
                    + NAVIGATION,
                )
                return

            payment = PaymentService.create_checkout(
                order,
            )
        except Exception as exc:
            if isinstance(exc, requests.RequestException):
                reason = (
                    "Nomba could not be reached from this server right now. "
                    "If you are testing live, confirm NOMBA_BASE_URL uses https://api.nomba.com/v1. "
                    "If you are testing sandbox, confirm the server has internet/DNS access to https://sandbox.nomba.com/v1."
                )
            else:
                reason = str(exc)

            WhatsAppService.send_text(
                phone,
                f"""We could not start payment yet.

Reason: {reason}

Your cart is still safe. Please try again or type cart."""
                + NAVIGATION,
            )
            return

        CartService.clear_cart(
            customer,
        )

        StateService.set_order(
            conversation,
            order,
        )

        StateService.set(
            conversation,
            PAYMENT,
            push=True,
        )

        WhatsAppService.send_url_button(
            phone,
            f"""💳 *Payment*

Order: *{order.checkout_reference}*
Food: {money(order.subtotal)}
Delivery: {money(order.delivery_fee)}
Deli customer fee: {money(order.customer_service_fee)}
Maintenance fee: {money(order.maintenance_fee)}
Total: {money(order.total)}

We use Nomba for secure payments.

Tap Continue to pay in your browser. After payment, Deli will confirm the restaurant and delivery rider.""",
            "Continue",
            payment.checkout_url,
            fallback_text=f"""💳 *Payment*

Order: *{order.checkout_reference}*
Food: {money(order.subtotal)}
Delivery: {money(order.delivery_fee)}
Deli customer fee: {money(order.customer_service_fee)}
Maintenance fee: {money(order.maintenance_fee)}
Total: {money(order.total)}

Pay securely with Nomba:
{payment.checkout_url}""",
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
