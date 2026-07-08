from decimal import Decimal

from django.utils.dateparse import parse_time

from users.constants import (
    ASK_LOCATION,
    ASK_NAME,
    ASK_ROLE,
    BROWSE_RESTAURANTS,
    BUSINESS_HOME,
    CHECKOUT,
    CHECKOUT_ASK_NAME,
    CONFIRM_DELIVERY_DETAILS,
    DELISEND_CONFIRMATION,
    HOME,
    ORDER_STATUS,
    PAYMENT,
    RATE_ORDER,
    RESTAURANT_ADMIN,
    REGISTER_RESTAURANT,
    REGISTER_RIDER,
    REVIEW_CHOICE,
    RIDER_ADMIN,
    SEARCH_RESTAURANTS,
    SELECT_DELIVERY_RIDER,
    CONFIRM_TYPED_ORDER,
    TYPE_ORDER,
    VIEW_CART,
    VIEW_ITEM,
    VIEW_MENU,
)

from cart.services.cart_service import CartService
from delivery.models import DeliveryRider
from locations.models import Area
from orders.models import Order
from orders.services.order_service import OrderService
from restaurants.models import (
    Category,
    Inventory,
    MenuItem,
    MenuItemReview,
    OpeningHour,
    Restaurant,
    RestaurantReview,
)

from .customer_service import CustomerService
from .formatting import money
from .home_handler import HomeHandler
from .navigation_service import NavigationService
from .state_service import StateService
from .whatsapp_service import WhatsAppService

from whatsapp.constants import NAVIGATION
from whatsapp.handlers.cart import CartHandler
from whatsapp.handlers.checkout import CheckoutHandler
from whatsapp.handlers.location import LocationHandler
from whatsapp.handlers.menu import MenuHandler
from whatsapp.handlers.restaurant import RestaurantHandler
from whatsapp.handlers.search_handler import SearchHandler
from whatsapp.handlers.typed_order import TypedOrderHandler


class RouterService:

    @classmethod
    def route(
        cls,
        phone,
        customer,
        conversation,
        message,
    ):

        OrderService.check_provider_timeouts()

        command = message.lower().strip()

        if not customer.account_type and command in (
            "0",
            "home",
            "menu",
            "start",
        ):
            StateService.set(
                conversation,
                ASK_ROLE,
            )
            return cls._prompt_role(
                phone,
            )

        if command in (
            "0",
            "home",
            "menu",
            "start",
        ):
            if customer.account_type in (
                customer.ACCOUNT_RESTAURANT,
                customer.ACCOUNT_RIDER,
            ):
                StateService.reset(
                    conversation,
                    BUSINESS_HOME,
                )
                return cls._show_business_home(
                    phone,
                    customer,
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

        if command in (
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

        if command == "clear cart":
            CartService.clear_cart(customer)
            StateService.reset(
                conversation,
                HOME,
            )
            WhatsAppService.send_text(
                phone,
                "🗑️ Cart cleared.",
            )
            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

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

        if command == "back":
            previous = cls._go_back(conversation)
            return cls._render_state(
                phone,
                customer,
                conversation,
                previous,
            )

        if command in (
            "orders",
            "my orders",
        ):
            StateService.set(
                conversation,
                ORDER_STATUS,
                push=True,
            )
            return cls._show_orders(
                phone,
                customer,
            )

        if command in (
            "track",
            "track order",
            "track_order",
            "where is my order",
            "paid",
            "i have paid",
            "payment successful",
            "payment success",
            "successful payment",
        ):
            StateService.set(
                conversation,
                ORDER_STATUS,
                push=True,
            )
            return cls._handle_order_status_action(
                phone,
                customer,
                conversation,
                "track_order",
            )

        state = StateService.get(
            conversation,
        )

        if not customer.account_type and state != ASK_ROLE:
            StateService.set(
                conversation,
                ASK_ROLE,
            )
            return cls._prompt_role(
                phone,
            )

        if state == ASK_ROLE:
            return cls._handle_role_selection(
                phone,
                customer,
                conversation,
                command,
            )

        if state == ASK_LOCATION:
            return LocationHandler().handle(
                phone,
                message,
            )

        if state == ASK_NAME:
            CustomerService.save_name(
                customer,
                message,
            )
            StateService.set(
                conversation,
                ASK_LOCATION,
            )
            WhatsAppService.send_text(
                phone,
                f"✅ Name saved, {customer.name}.",
            )
            return WhatsAppService.request_location(
                phone,
            )

        if state == CHECKOUT_ASK_NAME:
            CustomerService.save_name(
                customer,
                message,
            )
            WhatsAppService.send_text(
                phone,
                f"✅ Name saved, {customer.name}.",
            )
            return CheckoutHandler().start_checkout(
                phone,
                conversation,
            )

        if state == BUSINESS_HOME:
            return cls._handle_business_home(
                phone,
                customer,
                conversation,
                command,
            )

        if state == RESTAURANT_ADMIN:
            return cls._handle_restaurant_admin(
                phone,
                customer,
                command,
                message,
            )

        if state == RIDER_ADMIN:
            return cls._handle_rider_admin(
                phone,
                customer,
                command,
            )

        if state == HOME:
            return cls._handle_home(
                phone,
                customer,
                conversation,
                command,
            )

        if state in (
            TYPE_ORDER,
            CONFIRM_TYPED_ORDER,
        ):
            return TypedOrderHandler().handle(
                phone,
                customer,
                conversation,
                message,
            )

        if state == SEARCH_RESTAURANTS:
            return SearchHandler().handle(
                phone,
                message,
            )

        if state == BROWSE_RESTAURANTS:
            return MenuHandler().handle(
                phone,
                message,
            )

        if state == VIEW_MENU:
            if message.strip():
                return CheckoutHandler().handle(
                    phone,
                    message,
                )
            return MenuHandler().handle(
                phone,
                "",
            )

        if state == VIEW_ITEM:
            return CheckoutHandler().handle(
                phone,
                message,
            )

        if state == VIEW_CART:
            return CartHandler().handle(
                phone,
                message,
            )

        if state in (
            CHECKOUT,
            CONFIRM_DELIVERY_DETAILS,
            SELECT_DELIVERY_RIDER,
        ):
            return CheckoutHandler().handle(
                phone,
                message,
            )

        if state == PAYMENT:
            return cls._handle_payment_wait(
                phone,
            )

        if state == ORDER_STATUS:
            return cls._handle_order_status_action(
                phone,
                customer,
                conversation,
                command,
            )

        if state == REGISTER_RESTAURANT:
            return cls._register_restaurant(
                phone,
                customer,
                conversation,
                message,
            )

        if state == REGISTER_RIDER:
            return cls._register_rider(
                phone,
                customer,
                conversation,
                message,
            )

        if state == RATE_ORDER:
            return cls._handle_review(
                phone,
                customer,
                conversation,
                message,
            )

        if state == REVIEW_CHOICE:
            return cls._handle_review_choice(
                phone,
                customer,
                conversation,
                command,
            )

        if state == DELISEND_CONFIRMATION:
            return cls._handle_delisend_confirmation(
                phone,
                conversation,
                command,
            )

        StateService.reset(
            conversation,
            BUSINESS_HOME,
        )
        return cls._show_business_home(
            phone,
            customer,
        )

    @staticmethod
    def _prompt_role(phone):

        WhatsAppService.send_buttons(
            phone,
            """👋 *Welcome to Deli*

Choose how this WhatsApp number should be used.

You can register one account type per number. To switch later, contact Deli support to delete the account.""",
            [
                ("1", "Customer"),
                ("2", "Restaurant"),
                ("3", "Delivery Rider"),
            ],
            "You can still reply 1, 2, or 3.",
        )


    @classmethod
    def _handle_role_selection(
        cls,
        phone,
        customer,
        conversation,
        command,
    ):

        if command in (
            "1",
            "customer",
            "order food",
        ):
            customer.account_type = customer.ACCOUNT_CUSTOMER
            customer.save(
                update_fields=[
                    "account_type",
                    "updated_at",
                ]
            )
            StateService.set(
                conversation,
                ASK_LOCATION,
            )
            return WhatsAppService.request_location(phone)

        if command in (
            "2",
            "restaurant",
            "vendor",
        ):
            customer.account_type = customer.ACCOUNT_RESTAURANT
            customer.save(
                update_fields=[
                    "account_type",
                    "updated_at",
                ]
            )
            StateService.set(
                conversation,
                REGISTER_RESTAURANT,
            )
            return cls._prompt_restaurant_registration(
                phone,
            )

        if command in (
            "3",
            "rider",
            "delivery",
            "delivery rider",
        ):
            customer.account_type = customer.ACCOUNT_RIDER
            customer.save(
                update_fields=[
                    "account_type",
                    "updated_at",
                ]
            )
            StateService.set(
                conversation,
                REGISTER_RIDER,
            )
            return cls._prompt_rider_registration(
                phone,
            )

        return cls._prompt_role(phone)

    @classmethod
    def _show_business_home(
        cls,
        phone,
        customer,
    ):

        title = (
            "Restaurant"
            if customer.account_type == customer.ACCOUNT_RESTAURANT
            else "Delivery Rider"
        )

        WhatsAppService.send_buttons(
            phone,
            f"""🏠 *Deli {title}*

Choose where you want to go.""",
            [
                ("1", "Admin"),
                ("2", "Order Food"),
            ],
            "Type home anytime to return here.",
        )

    @classmethod
    def _handle_business_home(
        cls,
        phone,
        customer,
        conversation,
        command,
    ):

        if command in (
            "1",
            "admin",
            "login as admin",
        ):
            if customer.account_type == customer.ACCOUNT_RESTAURANT:
                StateService.set(
                    conversation,
                    RESTAURANT_ADMIN,
                )
                return cls._show_restaurant_admin(
                    phone,
                    customer,
                )

            StateService.set(
                conversation,
                RIDER_ADMIN,
            )
            return cls._show_rider_admin(
                phone,
                customer,
            )

        if command in (
            "2",
            "order",
            "order food",
            "customer",
        ):
            StateService.set_business_ordering(
                conversation,
                True,
            )
            StateService.set(
                conversation,
                HOME,
            )
            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

        return cls._show_business_home(
            phone,
            customer,
        )

    @classmethod
    def _show_restaurant_admin(
        cls,
        phone,
        customer,
    ):

        restaurant = cls._restaurant_for_customer(customer)

        if not restaurant:
            WhatsAppService.send_text(
                phone,
                "No restaurant profile found for this number. Type home and contact Deli support if this is wrong.",
            )
            return

        status = "Open" if restaurant.is_active else "Closed"

        WhatsAppService.send_text(
            phone,
            f"""🏪 *{restaurant.name} Admin*

Status: {status}
Prep time: {restaurant.estimated_prep_minutes} minutes

Reply with a number:

1️⃣ Status, hours and prep time
2️⃣ Menu and inventory
3️⃣ Add or edit meals
4️⃣ Open orders
5️⃣ Profile and photos

Fast commands:
open
closed
orders
sold out ITEM NAME
available ITEM NAME
inventory ITEM NAME = 10

Type home to leave admin."""
        )

    @classmethod
    def _handle_restaurant_admin(
        cls,
        phone,
        customer,
        command,
        message,
    ):

        restaurant = cls._restaurant_for_customer(customer)

        if not restaurant:
            return cls._show_restaurant_admin(
                phone,
                customer,
            )

        if command in (
            "1",
            "status",
            "hours",
            "opening hours",
            "prep",
            "prep time",
        ):
            return cls._show_restaurant_status_help(
                phone,
                customer,
                restaurant,
            )

        if command in (
            "2",
            "menu",
            "inventory",
            "stock",
        ):
            return cls._show_restaurant_inventory(
                phone,
                customer,
                restaurant,
            )

        if command in (
            "3",
            "add meal",
            "edit meal",
            "meal",
            "products",
        ):
            return cls._show_meal_edit_help(
                phone,
                customer,
                restaurant,
            )

        if command.startswith("add meal"):
            return cls._add_or_update_meal(
                phone,
                customer,
                restaurant,
                message,
            )

        if command.startswith("meal\n"):
            return cls._add_or_update_meal(
                phone,
                customer,
                restaurant,
                message,
            )

        if command.startswith("price "):
            return cls._update_menu_item_price(
                phone,
                customer,
                restaurant,
                message[6:].strip(),
            )

        if command.startswith("prep "):
            return cls._update_prep_time(
                phone,
                customer,
                restaurant,
                message[5:].strip(),
            )

        if command.startswith("hours "):
            return cls._update_opening_hours(
                phone,
                customer,
                restaurant,
                message[6:].strip(),
            )

        if command.startswith("closed day "):
            return cls._close_opening_day(
                phone,
                customer,
                restaurant,
                message[11:].strip(),
            )

        if command in (
            "4",
            "orders",
            "open orders",
            "pending orders",
        ):
            return cls._show_restaurant_orders(
                phone,
                customer,
                restaurant,
            )

        if command in (
            "5",
            "profile",
            "photos",
            "images",
        ):
            return cls._show_restaurant_profile_help(
                phone,
                customer,
                restaurant,
            )

        if command.startswith("profile\n"):
            return cls._update_restaurant_profile(
                phone,
                customer,
                restaurant,
                message,
            )

        if command in (
            "open",
            "available",
        ):
            restaurant.is_active = True
            restaurant.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ]
            )
            WhatsAppService.send_text(phone, "✅ Restaurant is open.")
            return cls._show_restaurant_admin(phone, customer)

        if command in (
            "closed",
            "close",
            "busy",
        ):
            restaurant.is_active = False
            restaurant.save(
                update_fields=[
                    "is_active",
                    "updated_at",
                ]
            )
            WhatsAppService.send_text(phone, "✅ Restaurant is closed.")
            return cls._show_restaurant_admin(phone, customer)

        if command.startswith("sold out "):
            return cls._set_menu_item_availability(
                phone,
                customer,
                restaurant,
                message[9:].strip(),
                False,
            )

        if command.startswith("unavailable "):
            return cls._set_menu_item_availability(
                phone,
                customer,
                restaurant,
                message[12:].strip(),
                False,
            )

        if command.startswith("available "):
            return cls._set_menu_item_availability(
                phone,
                customer,
                restaurant,
                message[10:].strip(),
                True,
            )

        if command.startswith("inventory "):
            return cls._update_inventory(
                phone,
                customer,
                restaurant,
                message[10:].strip(),
            )

        return cls._show_restaurant_admin(
            phone,
            customer,
        )

    @classmethod
    def _show_rider_admin(
        cls,
        phone,
        customer,
    ):

        rider = cls._rider_for_customer(customer)

        if not rider:
            WhatsAppService.send_text(
                phone,
                "No delivery rider profile found for this number. Type home and contact Deli support if this is wrong.",
            )
            return

        status = "Available" if rider.is_available else "Busy"

        WhatsAppService.send_text(
            phone,
            f"""🏍️ *{rider.name} Admin*

Status: {status}

Reply with a number:

1️⃣ Status
2️⃣ Pending deliveries
3️⃣ Profile and pricing

Fast commands:
available
busy
closed
fee 1500
vehicle Bike

Type home to leave admin."""
        )

    @classmethod
    def _handle_rider_admin(
        cls,
        phone,
        customer,
        command,
    ):

        rider = cls._rider_for_customer(customer)

        if not rider:
            return cls._show_rider_admin(
                phone,
                customer,
            )

        if command in (
            "1",
            "status",
        ):
            return cls._show_rider_admin(
                phone,
                customer,
            )

        if command in (
            "2",
            "orders",
            "jobs",
            "pending deliveries",
            "deliveries",
        ):
            return cls._show_rider_jobs(
                phone,
                customer,
                rider,
            )

        if command in (
            "3",
            "profile",
            "pricing",
        ):
            return cls._show_rider_profile_help(
                phone,
                customer,
                rider,
            )

        if command.startswith("fee "):
            return cls._update_rider_fee(
                phone,
                customer,
                rider,
                command[4:].strip(),
            )

        if command.startswith("vehicle "):
            return cls._update_rider_vehicle(
                phone,
                customer,
                rider,
                message[8:].strip(),
            )

        if command in (
            "available",
            "open",
            "online",
        ):
            rider.is_available = True
            rider.save(
                update_fields=[
                    "is_available",
                    "updated_at",
                ]
            )
            WhatsAppService.send_text(phone, "✅ You are available.")
            return cls._show_rider_admin(phone, customer)

        if command in (
            "busy",
            "closed",
            "close",
            "offline",
        ):
            rider.is_available = False
            rider.save(
                update_fields=[
                    "is_available",
                    "updated_at",
                ]
            )
            WhatsAppService.send_text(phone, "✅ You are marked busy.")
            return cls._show_rider_admin(phone, customer)

        return cls._show_rider_admin(phone, customer)

    @classmethod
    def _handle_home(
        cls,
        phone,
        customer,
        conversation,
        command,
    ):

        if command in (
            "1",
            "type order",
            "typed order",
            "quick order",
            "order",
        ):
            return TypedOrderHandler().start(
                phone,
                customer,
                conversation,
            )

        if command in (
            "2",
            "browse",
            "browse restaurants",
            "restaurant",
            "restaurants",
        ):
            return RestaurantHandler().handle(
                phone,
                "",
            )

        if command in (
            "3",
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

Type the food or restaurant name."""
                + NAVIGATION,
            )
            return

        if command in (
            "4",
            "orders",
            "my orders",
            "track",
            "track order",
            "where is my order",
        ):
            StateService.set(
                conversation,
                ORDER_STATUS,
                push=True,
            )
            return cls._show_orders(
                phone,
                customer,
            )

        if command in (
            "5",
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

        if command in (
            "review",
            "rate",
            "leave review",
        ):
            return cls._start_review(
                phone,
                customer,
                conversation,
            )

        return HomeHandler.show(
            phone,
            customer,
            conversation,
        )

    @classmethod
    def _go_back(cls, conversation):

        previous = NavigationService.back(
            conversation,
        )

        if previous in (
            HOME,
            BROWSE_RESTAURANTS,
        ):
            conversation.selected_restaurant = None
            conversation.selected_menu_item = None
        elif previous == VIEW_MENU:
            conversation.selected_menu_item = None

        conversation.current_step = previous
        conversation.save(
            update_fields=[
                "current_step",
                "selected_restaurant",
                "selected_menu_item",
                "updated_at",
            ]
        )

        return previous

    @classmethod
    def _render_state(
        cls,
        phone,
        customer,
        conversation,
        state,
    ):

        if state == HOME:
            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

        if state == BROWSE_RESTAURANTS:
            return RestaurantHandler().handle(
                phone,
                "",
            )

        if state == VIEW_MENU:
            return MenuHandler().handle(
                phone,
                "",
            )

        if state == VIEW_CART:
            return CartHandler().handle(
                phone,
                "",
            )

        if state == CHECKOUT:
            return CheckoutHandler().start_checkout(
                phone,
                conversation,
            )

        StateService.reset(
            conversation,
            BUSINESS_HOME,
        )
        return cls._show_business_home(
            phone,
            customer,
        )

    @classmethod
    def _show_orders(
        cls,
        phone,
        customer,
    ):

        orders = cls._recent_customer_orders(customer)

        if not orders:
            WhatsAppService.send_text(
                phone,
                """📦 *My Orders*

You don't have any orders yet.

Reply 1 to browse restaurants."""
                + NAVIGATION,
            )
            return

        conversation = customer.conversation
        conversation.selected_order = None
        conversation.save(
            update_fields=[
                "selected_order",
                "updated_at",
            ]
        )

        rows = []
        text = "📦 *My Orders*\n\nChoose an order to track.\n\n"

        for index, order in enumerate(orders, start=1):
            text += (
                f"{index}. *{order.checkout_reference}*\n"
                f"{order.restaurant.name}\n"
                f"Status: {order.get_status_display()}\n"
                f"Total: {money(order.total)}\n\n"
            )
            rows.append(
                (
                    f"order:{order.id}",
                    f"Order {index}",
                    f"{order.restaurant.name} · {order.get_status_display()}",
                )
            )

        rows.append(
            (
                "home",
                "Keep Shopping",
                "Back to the main menu",
            )
        )

        WhatsAppService.send_list(
            phone,
            text,
            rows,
            "Choose order",
            "You can also reply with the order number.",
        )

    @classmethod
    def _recent_customer_orders(cls, customer):

        return list(
            customer.orders.select_related(
                "restaurant",
                "delivery_rider",
            ).prefetch_related(
                "items",
            ).order_by(
                "-created_at",
            )[:5]
        )

    @classmethod
    def _latest_trackable_order(cls, customer):

        orders = cls._recent_customer_orders(customer)

        for order in orders:
            if order.status not in (
                Order.STATUS_CANCELLED,
                Order.STATUS_DELIVERED,
            ):
                return order

        return orders[0] if orders else None

    @classmethod
    def _order_from_command(
        cls,
        customer,
        command,
    ):

        orders = cls._recent_customer_orders(customer)

        if command.startswith("order:"):
            try:
                order_id = int(
                    command.split(
                        ":",
                        1,
                    )[1]
                )
            except (IndexError, ValueError):
                return None

            for order in orders:
                if order.id == order_id:
                    return order

            return None

        if command.isdigit():
            index = int(command) - 1
            if 0 <= index < len(orders):
                return orders[index]

        return None

    @classmethod
    def _show_order_actions(
        cls,
        phone,
        customer,
        conversation,
        order,
    ):

        StateService.set_order(
            conversation,
            order,
        )
        StateService.set(
            conversation,
            ORDER_STATUS,
        )

        WhatsAppService.send_list(
            phone,
            OrderService.order_tracking_text(order),
            OrderService.post_payment_action_rows(),
            "Order actions",
            "Reply 1, 2, 3, 4, or 5.",
        )

    @classmethod
    def _handle_order_status_action(
        cls,
        phone,
        customer,
        conversation,
        command,
    ):

        selected_order = None

        if command.startswith("order:") or (
            command.isdigit()
            and not conversation.selected_order
        ):
            selected_order = cls._order_from_command(
                customer,
                command,
            )

        if selected_order:
            return cls._show_order_actions(
                phone,
                customer,
                conversation,
                selected_order,
            )

        order = (
            conversation.selected_order
            or cls._latest_trackable_order(customer)
        )

        if not order:
            return cls._show_orders(
                phone,
                customer,
            )

        if command in (
            "1",
            "track",
            "track order",
            "track_order",
            "where is my order",
            "payment successful",
            "payment success",
        ):
            return cls._show_order_actions(
                phone,
                customer,
                conversation,
                order,
            )

        if command in (
            "2",
            "confirm delivered",
            "confirm_delivered",
            "delivered",
            "meal delivered",
        ):
            if order.status == Order.STATUS_DELIVERED:
                WhatsAppService.send_text(
                    phone,
                    f"✅ Order *{order.checkout_reference}* is already marked delivered.",
                )
                return cls._show_order_actions(
                    phone,
                    customer,
                    conversation,
                    order,
                )

            OrderService.mark_delivered(order)
            return

        if command in (
            "3",
            "review",
            "rate",
        ):
            StateService.set_order(
                conversation,
                order,
            )
            return cls._start_review(
                phone,
                customer,
                conversation,
            )

        if command in (
            "4",
            "end",
            "end session",
            "end_session",
            "endsession",
        ):
            StateService.reset(
                conversation,
                HOME,
            )
            WhatsAppService.send_text(
                phone,
                "✅ Session ended. Type hey whenever you want to order again.",
            )
            return

        if command in (
            "5",
            "home",
            "keep shopping",
            "keep_shopping",
            "shop",
        ):
            StateService.reset(
                conversation,
                HOME,
            )
            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

        return cls._show_orders(
            phone,
            customer,
        )

    @staticmethod
    def _handle_payment_wait(phone):

        WhatsAppService.send_text(
            phone,
            """💳 Payment is pending.

Once Nomba confirms payment, Deli will automatically contact the restaurant and delivery rider."""
            + NAVIGATION,
        )

    @staticmethod
    def _prompt_restaurant_registration(phone):

        WhatsAppService.send_text(
            phone,
            """🏪 *Register Restaurant*

Send all details in one message:

Name:
Contact:
Restaurant Phone:
WhatsApp:
Cuisine:
Address:
Bank Name:
Bank Code:
Account Number:
Account Name:

Example:
Name: Adaeze Kitchen
Contact: Adaeze
Restaurant Phone: 08011112222
WhatsApp: 2348011112222
Cuisine: Local meals
Address: 12 Admiralty Way, Lekki
Bank Name: Wema Bank
Bank Code: 035
Account Number: 0000000000
Account Name: Adaeze Kitchen"""
            + NAVIGATION,
        )

    @classmethod
    def _register_restaurant(
        cls,
        phone,
        customer,
        conversation,
        message,
    ):

        data = cls._parse_key_value_message(
            message,
        )

        name = data.get("name", "")
        restaurant_phone = (
            data.get("restaurant phone")
            or data.get("phone")
            or phone
        )
        whatsapp = data.get("whatsapp") or restaurant_phone
        address = data.get("address", "")

        area = cls._default_area(customer)

        if not name or not address or not area:
            WhatsAppService.send_text(
                phone,
                "Please include Name and Address. Also make sure your customer location is set first."
                + NAVIGATION,
            )
            return

        restaurant, created = Restaurant.objects.update_or_create(
            phone=restaurant_phone,
            defaults={
                "name": name,
                "contact_name": data.get("contact", ""),
                "whatsapp_number": whatsapp,
                "cuisine_type": data.get("cuisine", ""),
                "description": data.get("description", ""),
                "address": address,
                "area": area,
                "bank_name": data.get("bank name", ""),
                "bank_code": data.get("bank code", ""),
                "account_number": data.get("account number", ""),
                "account_name": data.get("account name", ""),
                "is_active": True,
                "is_verified": False,
            },
        )

        StateService.reset(
            conversation,
            BUSINESS_HOME,
        )

        action = "created" if created else "updated"

        WhatsAppService.send_text(
            phone,
            f"""✅ Restaurant profile {action}.

{restaurant.name} is saved. You can finish menus and images from the simple dashboard or Django admin."""
        )

        return cls._show_business_home(
            phone,
            customer,
        )

    @staticmethod
    def _prompt_rider_registration(phone):

        WhatsAppService.send_text(
            phone,
            """🏍️ *Register Delivery Rider*

Send all details in one message:

Name:
Phone:
WhatsApp:
Vehicle:
Base Fee:
Bank Name:
Bank Code:
Account Number:
Account Name:

Example:
Name: Tunde Express
Phone: 08033334444
WhatsApp: 2348033334444
Vehicle: Bike
Base Fee: 1500
Bank Name: Wema Bank
Bank Code: 035
Account Number: 0000000000
Account Name: Tunde Express"""
            + NAVIGATION,
        )

    @classmethod
    def _register_rider(
        cls,
        phone,
        customer,
        conversation,
        message,
    ):

        data = cls._parse_key_value_message(
            message,
        )

        name = data.get("name", "")
        rider_phone = data.get("phone") or phone
        whatsapp = data.get("whatsapp") or rider_phone

        if not name:
            WhatsAppService.send_text(
                phone,
                "Please include Name."
                + NAVIGATION,
            )
            return

        base_fee = cls._decimal(
            data.get("base fee"),
            Decimal("1500.00"),
        )

        rider, created = DeliveryRider.objects.update_or_create(
            phone=rider_phone,
            defaults={
                "name": name,
                "whatsapp_number": whatsapp,
                "area": cls._default_area(customer),
                "vehicle_type": data.get("vehicle", "Bike"),
                "base_fee": base_fee,
                "bank_name": data.get("bank name", ""),
                "bank_code": data.get("bank code", ""),
                "account_number": data.get("account number", ""),
                "account_name": data.get("account name", ""),
                "is_active": True,
                "is_available": True,
            },
        )

        StateService.reset(
            conversation,
            HOME,
        )

        action = "created" if created else "updated"

        WhatsAppService.send_text(
            phone,
            f"✅ Delivery rider profile {action}: {rider.name}."
        )

        return HomeHandler.show(
            phone,
            customer,
            conversation,
        )

    @classmethod
    def _handle_review(
        cls,
        phone,
        customer,
        conversation,
        message,
    ):

        order = conversation.selected_order

        if not order:
            StateService.reset(
                conversation,
                HOME,
            )
            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

        parts = message.strip().split(
            " ",
            2,
        )

        try:
            first = parts[0].replace("-", "")
            review_type = (
                conversation.search_result_type[0]
                if conversation.search_result_type
                else "restaurant_review"
            )

            if review_type == "food_review":
                item_index = int(first) - 1
                rating = Decimal(parts[1])
                comment = parts[2].lstrip("- ").strip() if len(parts) > 2 else ""
            else:
                item_index = None
                rating = Decimal(first)
                comment = parts[1].lstrip("- ").strip() if len(parts) > 1 else ""
        except (ValueError, IndexError):
            WhatsAppService.send_text(
                phone,
                "Please reply with a rating from 1.0 to 5.0."
            )
            return

        if rating < Decimal("1.0") or rating > Decimal("5.0"):
            WhatsAppService.send_text(
                phone,
                "Please reply with a rating from 1.0 to 5.0."
            )
            return

        if (
            conversation.search_result_type
            and conversation.search_result_type[0] == "food_review"
        ):
            ids = conversation.search_result_ids or []

            if item_index is None or item_index < 0 or item_index >= len(ids):
                WhatsAppService.send_text(
                    phone,
                    "Meal number not found. Use: meal number rating comment"
                )
                return

            menu_item = MenuItem.objects.get(
                id=ids[item_index],
            )

            MenuItemReview.objects.create(
                order=order,
                customer=customer,
                menu_item=menu_item,
                rating=rating,
                comment=comment,
            )

            cls._recalculate_menu_item_rating(menu_item)
        else:
            RestaurantReview.objects.update_or_create(
                order=order,
                defaults={
                    "customer": customer,
                    "restaurant": order.restaurant,
                    "rating": rating,
                    "comment": comment,
                },
            )

            cls._recalculate_restaurant_rating(
                order.restaurant,
            )

        StateService.reset(
            conversation,
            HOME,
        )

        WhatsAppService.send_text(
            phone,
            "🙏 Thank you for the review."
        )

        return HomeHandler.show(
            phone,
            customer,
            conversation,
        )

    @staticmethod
    def _handle_delisend_confirmation(
        phone,
        conversation,
        command,
    ):

        order = conversation.selected_order

        if not order:
            return

        if command in (
            "yes",
            "y",
            "accept",
            "continue",
        ):
            OrderService.accept_delisend_fallback(
                order,
            )
            return

        if command in (
            "no",
            "n",
            "cancel",
        ):
            OrderService.decline_delisend_fallback(
                order,
            )
            return

        WhatsAppService.send_text(
            phone,
            "Reply YES to continue with Deli Dash or NO to cancel."
        )

    @classmethod
    def _start_review(
        cls,
        phone,
        customer,
        conversation,
    ):

        order = conversation.selected_order

        if (
            not order
            or order.status
            not in [
                Order.STATUS_DELIVERED,
                Order.STATUS_ACCEPTED,
                Order.STATUS_ON_THE_WAY,
            ]
        ):
            order = (
                customer.orders
                .filter(
                    status__in=[
                        Order.STATUS_DELIVERED,
                        Order.STATUS_ACCEPTED,
                        Order.STATUS_ON_THE_WAY,
                    ]
                )
                .select_related(
                    "restaurant",
                )
                .order_by(
                    "-created_at",
                )
                .first()
            )

        if not order:
            WhatsAppService.send_text(
                phone,
                "No recent order is ready for review yet."
                + NAVIGATION,
            )
            return

        StateService.set_order(
            conversation,
            order,
        )
        StateService.set(
            conversation,
            REVIEW_CHOICE,
        )

        WhatsAppService.send_buttons(
            phone,
            f"""Review order *{order.checkout_reference}*

Choose what you want to review.""",
            [
                ("1", "Review Meal"),
                ("2", "Restaurant"),
            ],
            "You can also reply 1 or 2.",
        )

    @classmethod
    def _handle_review_choice(
        cls,
        phone,
        customer,
        conversation,
        command,
    ):

        order = conversation.selected_order

        if not order:
            return cls._start_review(
                phone,
                customer,
                conversation,
            )

        if command == "1":
            items = list(
                order.items.select_related(
                    "menu_item",
                )
            )

            if not items:
                WhatsAppService.send_text(
                    phone,
                    "No meal items found for this order."
                )
                return

            conversation.search_result_ids = [
                item.menu_item_id
                for item in items
            ]
            conversation.search_result_type = [
                "food_review"
                for _ in items
            ]
            conversation.save(
                update_fields=[
                    "search_result_ids",
                    "search_result_type",
                    "updated_at",
                ]
            )

            text = "Which meal do you want to review?\n\n"

            for index, item in enumerate(items, start=1):
                text += f"{index}. {item.name}\n"

            text += "\nReply with: meal number rating comment\nExample: 1 4.5 spicy and nice"

            StateService.set(
                conversation,
                RATE_ORDER,
            )
            WhatsAppService.send_text(
                phone,
                text,
            )
            return

        if command == "2":
            conversation.search_result_type = ["restaurant_review"]
            conversation.save(
                update_fields=[
                    "search_result_type",
                    "updated_at",
                ]
            )
            StateService.set(
                conversation,
                RATE_ORDER,
            )
            WhatsAppService.send_text(
                phone,
                "Reply with a restaurant rating from 1.0 to 5.0 and optional comment.\nExample: 4.8 fast and tasty"
            )
            return

        WhatsAppService.send_text(
            phone,
            "Reply 1 to review a meal or 2 to review the restaurant."
        )

    @classmethod
    def _restaurant_for_customer(cls, customer):

        return Restaurant.objects.filter(
            phone=customer.phone,
        ).first() or Restaurant.objects.filter(
            whatsapp_number=customer.phone,
        ).first()

    @classmethod
    def _rider_for_customer(cls, customer):

        return DeliveryRider.objects.filter(
            phone=customer.phone,
        ).first() or DeliveryRider.objects.filter(
            whatsapp_number=customer.phone,
        ).first()

    @classmethod
    def _menu_item_for_restaurant(
        cls,
        restaurant,
        item_name,
    ):

        return (
            MenuItem.objects
            .filter(
                restaurant=restaurant,
                name__icontains=item_name,
            )
            .order_by(
                "name",
            )
            .first()
        )

    @classmethod
    def _set_menu_item_availability(
        cls,
        phone,
        customer,
        restaurant,
        item_name,
        is_available,
    ):

        item = cls._menu_item_for_restaurant(
            restaurant,
            item_name,
        )

        if not item:
            WhatsAppService.send_text(
                phone,
                "Meal item not found. Try the exact item name."
            )
            return cls._show_restaurant_admin(phone, customer)

        item.is_available = is_available
        item.save(
            update_fields=[
                "is_available",
            ]
        )

        WhatsAppService.send_text(
            phone,
            f"✅ {item.name} is now {'available' if is_available else 'sold out'}."
        )
        return cls._show_restaurant_admin(phone, customer)

    @classmethod
    def _update_inventory(
        cls,
        phone,
        customer,
        restaurant,
        payload,
    ):

        if "=" not in payload:
            WhatsAppService.send_text(
                phone,
                "Use: inventory ITEM NAME = 10"
            )
            return cls._show_restaurant_admin(phone, customer)

        item_name, quantity_text = payload.split("=", 1)

        item = cls._menu_item_for_restaurant(
            restaurant,
            item_name.strip(),
        )

        if not item:
            WhatsAppService.send_text(
                phone,
                "Meal item not found. Try the exact item name."
            )
            return cls._show_restaurant_admin(phone, customer)

        try:
            quantity = int(quantity_text.strip())
        except ValueError:
            WhatsAppService.send_text(
                phone,
                "Inventory quantity must be a whole number."
            )
            return cls._show_restaurant_admin(phone, customer)

        inventory, _ = Inventory.objects.get_or_create(
            menu_item=item,
        )
        inventory.quantity = max(quantity, 0)
        inventory.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )

        item.is_available = inventory.quantity > 0
        item.save(
            update_fields=[
                "is_available",
            ]
        )

        WhatsAppService.send_text(
            phone,
            f"✅ {item.name} inventory is now {inventory.quantity}."
        )
        return cls._show_restaurant_admin(phone, customer)

    @classmethod
    def _show_restaurant_status_help(
        cls,
        phone,
        customer,
        restaurant,
    ):

        hours = restaurant.opening_hours.all()
        hours_text = ""

        if hours:
            hours_text = "\n\nOpening hours:\n"
            for row in hours:
                hours_text += (
                    f"{row.day}: "
                    f"{'Closed' if row.is_closed else f'{row.opening_time} - {row.closing_time}'}\n"
                )

        WhatsAppService.send_text(
            phone,
            f"""🕒 *Status, Hours and Prep Time*

Current status: {'Open' if restaurant.is_active else 'Closed'}
Prep time: {restaurant.estimated_prep_minutes} minutes{hours_text}

Commands:
open
closed
prep 30
hours MON 09:00-21:00
closed day SUN"""
        )

    @classmethod
    def _show_restaurant_inventory(
        cls,
        phone,
        customer,
        restaurant,
    ):

        items = list(
            restaurant.menu_items.select_related(
                "category",
            ).order_by(
                "category__name",
                "name",
            )[:50]
        )

        if not items:
            return cls._show_meal_edit_help(
                phone,
                customer,
                restaurant,
            )

        text = "🍽️ *Menu and Inventory*\n\n"

        for item in items:
            stock = (
                item.inventory.quantity
                if hasattr(item, "inventory")
                else "not set"
            )
            status = "Available" if item.is_available else "Unavailable"
            text += (
                f"- {item.name} | {money(item.price)} | {status} | Stock: {stock}\n"
            )

        text += (
            "\nCommands:\n"
            "sold out ITEM NAME\n"
            "available ITEM NAME\n"
            "inventory ITEM NAME = 10\n"
            "price ITEM NAME = 2500"
        )

        WhatsAppService.send_text(
            phone,
            text,
        )

    @staticmethod
    def _show_meal_edit_help(
        phone,
        customer,
        restaurant,
    ):

        WhatsAppService.send_text(
            phone,
            """➕ *Add or Edit Meal*

Send one message like this:

add meal
Name: Smoky Jollof Rice
Price: 2500
Category: Rice Meals
Description: Party-style jollof with chicken
Stock: 20
Available: yes

Other commands:
price Smoky Jollof Rice = 2800
Send image with caption "meal Smoky Jollof Rice" to update the photo."""
        )

    @classmethod
    def _add_or_update_meal(
        cls,
        phone,
        customer,
        restaurant,
        message,
    ):

        lines = message.splitlines()

        if lines and lines[0].strip().lower() in ("add meal", "meal"):
            message = "\n".join(lines[1:])

        data = cls._parse_key_value_message(
            message,
        )

        name = data.get("name", "").strip()
        price = cls._decimal(
            data.get("price"),
            None,
        )

        if not name or price is None:
            WhatsAppService.send_text(
                phone,
                "Please include Name and Price."
            )
            return cls._show_meal_edit_help(phone, customer, restaurant)

        category = None
        category_name = data.get("category", "").strip()

        if category_name:
            category, _ = Category.objects.get_or_create(
                restaurant=restaurant,
                name=category_name,
            )

        available_text = data.get("available", "yes").lower().strip()

        item, created = MenuItem.objects.update_or_create(
            restaurant=restaurant,
            name=name,
            defaults={
                "category": category,
                "description": data.get("description", ""),
                "price": price,
                "is_available": available_text not in (
                    "no",
                    "false",
                    "sold out",
                    "unavailable",
                ),
            },
        )

        if data.get("stock") is not None:
            try:
                quantity = int(data.get("stock", "0").strip())
            except ValueError:
                quantity = 0

            inventory, _ = Inventory.objects.get_or_create(
                menu_item=item,
            )
            inventory.quantity = max(quantity, 0)
            inventory.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

            if inventory.quantity == 0:
                item.is_available = False
                item.save(
                    update_fields=[
                        "is_available",
                    ]
                )

        WhatsAppService.send_text(
            phone,
            f"✅ Meal {'created' if created else 'updated'}: {item.name}."
        )
        return cls._show_restaurant_inventory(phone, customer, restaurant)

    @classmethod
    def _update_menu_item_price(
        cls,
        phone,
        customer,
        restaurant,
        payload,
    ):

        if "=" not in payload:
            WhatsAppService.send_text(
                phone,
                "Use: price ITEM NAME = 2500"
            )
            return cls._show_restaurant_admin(phone, customer)

        item_name, price_text = payload.split("=", 1)
        item = cls._menu_item_for_restaurant(
            restaurant,
            item_name.strip(),
        )

        if not item:
            WhatsAppService.send_text(
                phone,
                "Meal item not found. Try the exact item name."
            )
            return cls._show_restaurant_admin(phone, customer)

        price = cls._decimal(
            price_text,
            None,
        )

        if price is None or price <= 0:
            WhatsAppService.send_text(
                phone,
                "Price must be greater than zero."
            )
            return cls._show_restaurant_admin(phone, customer)

        item.price = price
        item.save(
            update_fields=[
                "price",
            ]
        )

        WhatsAppService.send_text(
            phone,
            f"✅ {item.name} price is now {money(item.price)}."
        )
        return cls._show_restaurant_admin(phone, customer)

    @classmethod
    def _update_prep_time(
        cls,
        phone,
        customer,
        restaurant,
        payload,
    ):

        try:
            minutes = int(payload.strip())
        except ValueError:
            WhatsAppService.send_text(
                phone,
                "Use: prep 30"
            )
            return cls._show_restaurant_admin(phone, customer)

        restaurant.estimated_prep_minutes = max(minutes, 1)
        restaurant.save(
            update_fields=[
                "estimated_prep_minutes",
                "updated_at",
            ]
        )

        WhatsAppService.send_text(
            phone,
            f"✅ Prep time is now {restaurant.estimated_prep_minutes} minutes."
        )
        return cls._show_restaurant_admin(phone, customer)

    @classmethod
    def _update_opening_hours(
        cls,
        phone,
        customer,
        restaurant,
        payload,
    ):

        parts = payload.split(None, 1)

        if len(parts) != 2 or "-" not in parts[1]:
            WhatsAppService.send_text(
                phone,
                "Use: hours MON 09:00-21:00"
            )
            return cls._show_restaurant_admin(phone, customer)

        day = parts[0].upper()[:3]
        opening_text, closing_text = parts[1].split("-", 1)

        valid_days = {
            code
            for code, _ in OpeningHour.DAYS
        }

        opening_time = parse_time(opening_text.strip())
        closing_time = parse_time(closing_text.strip())

        if day not in valid_days or not opening_time or not closing_time:
            WhatsAppService.send_text(
                phone,
                "Use a valid day and 24-hour time, e.g. hours MON 09:00-21:00"
            )
            return cls._show_restaurant_admin(phone, customer)

        OpeningHour.objects.update_or_create(
            restaurant=restaurant,
            day=day,
            defaults={
                "opening_time": opening_time,
                "closing_time": closing_time,
                "is_closed": False,
            },
        )

        WhatsAppService.send_text(
            phone,
            f"✅ {day} hours saved: {opening_time} - {closing_time}."
        )
        return cls._show_restaurant_admin(phone, customer)

    @classmethod
    def _close_opening_day(
        cls,
        phone,
        customer,
        restaurant,
        payload,
    ):

        day = payload.upper()[:3]
        valid_days = {
            code
            for code, _ in OpeningHour.DAYS
        }

        if day not in valid_days:
            WhatsAppService.send_text(
                phone,
                "Use: closed day SUN"
            )
            return cls._show_restaurant_admin(phone, customer)

        OpeningHour.objects.update_or_create(
            restaurant=restaurant,
            day=day,
            defaults={
                "opening_time": parse_time("00:00"),
                "closing_time": parse_time("00:00"),
                "is_closed": True,
            },
        )

        WhatsAppService.send_text(
            phone,
            f"✅ {day} marked closed."
        )
        return cls._show_restaurant_admin(phone, customer)

    @classmethod
    def _show_restaurant_orders(
        cls,
        phone,
        customer,
        restaurant,
    ):

        orders = list(
            restaurant.orders.filter(
                status__in=[
                    Order.STATUS_PAID,
                    Order.STATUS_ACCEPTED,
                    Order.STATUS_PREPARING,
                    Order.STATUS_ON_THE_WAY,
                ]
            )
            .select_related(
                "customer",
                "delivery_rider",
            )
            .prefetch_related(
                "items",
            )
            .order_by(
                "-created_at",
            )[:10]
        )

        if not orders:
            WhatsAppService.send_text(
                phone,
                "No open restaurant orders right now."
            )
            return cls._show_restaurant_admin(phone, customer)

        text = "📦 *Open Orders*\n\n"

        for order in orders:
            text += (
                f"{order.checkout_reference}\n"
                f"Status: {order.get_status_display()}\n"
                f"Customer: {order.customer.name or order.customer.phone}\n"
                f"Items:\n{OrderService.order_items_text(order)}\n\n"
            )

        text += "When Deli asks Available?, reply YES or NO. Reply 1 after dispatch."

        WhatsAppService.send_text(
            phone,
            text,
        )

    @staticmethod
    def _show_restaurant_profile_help(
        phone,
        customer,
        restaurant,
    ):

        WhatsAppService.send_text(
            phone,
            f"""🏪 *Profile and Photos*

Current profile:
Name: {restaurant.name}
Cuisine: {restaurant.cuisine_type or "Not set"}
Address: {restaurant.address}
WhatsApp: {restaurant.whatsapp_number}

To update profile, send:
profile
Name: {restaurant.name}
Cuisine: Home Baker / Cake Seller / Meal Prep / Soup Vendor / Small Chops / Fruit Seller / Smoothie Seller
Address: your address
Contact: contact person
WhatsApp: 234XXXXXXXXXX

Photos:
Send image with caption "logo" to update restaurant logo.
Send image with caption "meal ITEM NAME" to update a meal photo."""
        )

    @classmethod
    def _update_restaurant_profile(
        cls,
        phone,
        customer,
        restaurant,
        message,
    ):

        lines = message.splitlines()

        if lines and lines[0].strip().lower() == "profile":
            message = "\n".join(lines[1:])

        data = cls._parse_key_value_message(
            message,
        )

        mapping = {
            "name": "name",
            "cuisine": "cuisine_type",
            "address": "address",
            "contact": "contact_name",
            "whatsapp": "whatsapp_number",
        }
        update_fields = []

        for key, field in mapping.items():
            value = data.get(key, "").strip()

            if value:
                setattr(
                    restaurant,
                    field,
                    value,
                )
                update_fields.append(field)

        if not update_fields:
            return cls._show_restaurant_profile_help(
                phone,
                customer,
                restaurant,
            )

        update_fields.append("updated_at")
        restaurant.save(
            update_fields=update_fields,
        )

        WhatsAppService.send_text(
            phone,
            "✅ Restaurant profile updated."
        )
        return cls._show_restaurant_admin(phone, customer)

    @classmethod
    def _show_rider_jobs(
        cls,
        phone,
        customer,
        rider,
    ):

        orders = list(
            rider.orders.filter(
                status__in=[
                    Order.STATUS_PAID,
                    Order.STATUS_ACCEPTED,
                    Order.STATUS_PREPARING,
                    Order.STATUS_ON_THE_WAY,
                ]
            )
            .select_related(
                "restaurant",
                "customer",
            )
            .prefetch_related(
                "items",
            )
            .order_by(
                "-created_at",
            )[:10]
        )

        if not orders:
            WhatsAppService.send_text(
                phone,
                "No pending delivery jobs right now."
            )
            return cls._show_rider_admin(phone, customer)

        text = "🏍️ *Pending Deliveries*\n\n"

        for order in orders:
            text += (
                f"{order.checkout_reference}\n"
                f"Status: {order.get_status_display()}\n"
                f"Restaurant: {order.restaurant.name}\n"
                f"Address: {order.delivery_address}\n"
                f"Phone: {order.delivery_contact_phone or order.customer.phone}\n\n"
            )

        text += "When Deli asks Available?, reply YES or NO. Reply 1 after delivery."

        WhatsAppService.send_text(
            phone,
            text,
        )

    @staticmethod
    def _show_rider_profile_help(
        phone,
        customer,
        rider,
    ):

        WhatsAppService.send_text(
            phone,
            f"""🏍️ *Rider Profile and Pricing*

Name: {rider.name}
Vehicle: {rider.vehicle_type}
Base fee: {money(rider.base_fee)}
Status: {'Available' if rider.is_available else 'Busy'}

Commands:
fee 1500
vehicle Bike
available
busy"""
        )

    @classmethod
    def _update_rider_fee(
        cls,
        phone,
        customer,
        rider,
        payload,
    ):

        fee = cls._decimal(
            payload,
            None,
        )

        if fee is None or fee < 0:
            WhatsAppService.send_text(
                phone,
                "Use: fee 1500"
            )
            return cls._show_rider_admin(phone, customer)

        rider.base_fee = fee
        rider.save(
            update_fields=[
                "base_fee",
                "updated_at",
            ]
        )

        WhatsAppService.send_text(
            phone,
            f"✅ Delivery fee updated to {money(rider.base_fee)}."
        )
        return cls._show_rider_admin(phone, customer)

    @classmethod
    def _update_rider_vehicle(
        cls,
        phone,
        customer,
        rider,
        payload,
    ):

        vehicle = payload.strip()

        if not vehicle:
            WhatsAppService.send_text(
                phone,
                "Use: vehicle Bike"
            )
            return cls._show_rider_admin(phone, customer)

        rider.vehicle_type = vehicle
        rider.save(
            update_fields=[
                "vehicle_type",
                "updated_at",
            ]
        )

        WhatsAppService.send_text(
            phone,
            f"✅ Vehicle updated to {rider.vehicle_type}."
        )
        return cls._show_rider_admin(phone, customer)

    @staticmethod
    def _parse_key_value_message(message):

        data = {}
        current_key = ""

        for raw_line in message.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            if ":" in line:
                key, value = line.split(
                    ":",
                    1,
                )
                current_key = key.strip().lower()
                data[current_key] = value.strip()
                continue

            if current_key:
                data[current_key] = (
                    f"{data[current_key]}\n{line}".strip()
                )

        return data

    @staticmethod
    def _default_area(customer):

        if customer.default_address and customer.default_address.area:
            return customer.default_address.area

        return Area.objects.first()

    @staticmethod
    def _decimal(value, default):

        if not value:
            return default

        try:
            return Decimal(
                str(value).replace(",", "").replace("₦", "").strip()
            )
        except Exception:
            return default

    @staticmethod
    def _recalculate_restaurant_rating(restaurant):

        reviews = restaurant.reviews.all()

        if not reviews.exists():
            return

        total_reviews = reviews.count()
        total_rating = sum(review.rating for review in reviews)

        restaurant.rating = (
            Decimal(total_rating) / Decimal(total_reviews)
        ).quantize(Decimal("0.01"))
        restaurant.total_reviews = total_reviews
        restaurant.save(
            update_fields=[
                "rating",
                "total_reviews",
                "updated_at",
            ]
        )

    @staticmethod
    def _recalculate_menu_item_rating(menu_item):

        reviews = menu_item.reviews.all()

        if not reviews.exists():
            return

        total_reviews = reviews.count()
        total_rating = sum(review.rating for review in reviews)

        menu_item.rating = (
            total_rating / Decimal(total_reviews)
        ).quantize(Decimal("0.01"))
        menu_item.total_reviews = total_reviews
        menu_item.save(
            update_fields=[
                "rating",
                "total_reviews",
            ]
        )
