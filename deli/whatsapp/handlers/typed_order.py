import re
from collections import defaultdict

from django.db.models import Q

from cart.services.cart_service import CartService
from restaurants.models import MenuItem
from restaurants.services.search_service import SearchService
from users.constants import CONFIRM_TYPED_ORDER, TYPE_ORDER, VIEW_CART
from whatsapp.constants import NAVIGATION
from whatsapp.services.formatting import money
from whatsapp.services.home_handler import HomeHandler
from whatsapp.services.state_service import StateService
from whatsapp.services.whatsapp_service import WhatsAppService

from .base import BaseHandler


class TypedOrderHandler(BaseHandler):
    """
    Deterministic typed-order flow.

    This intentionally avoids AI so the MVP can run on the same VPS without
    extra model/API costs. It only prices meals it can match to menu items in
    the customer's current area.
    """

    QUANTITY_WORDS = {
        "a": 1,
        "an": 1,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    UNIT_WORDS = (
        "plates?",
        "packs?",
        "pieces?",
        "orders?",
        "bottles?",
        "cups?",
        "servings?",
        "wraps?",
        "bowls?",
        "portions?",
        "of",
    )

    def start(
        self,
        phone,
        customer,
        conversation,
    ):

        StateService.set(
            conversation,
            TYPE_ORDER,
            push=True,
        )

        WhatsAppService.send_buttons(
            phone,
            """📝 *Type Your Order*

Send everything you want in one message.

Example:
3 plates of jollof rice, 2 cokes, 1 meat pie

Deli will match the items to menus near you, calculate the price, and ask you to confirm before checkout.""",
            [
                ("back", "Go Back"),
                ("2", "Search Food"),
                ("3", "Browse Menu"),
            ],
            "You can also type your order now.",
        )

    def handle(
        self,
        phone,
        customer,
        conversation,
        message,
    ):

        command = message.lower().strip()

        if conversation.current_step == CONFIRM_TYPED_ORDER:
            return self._handle_confirmation(
                phone,
                customer,
                conversation,
                command,
            )

        if command in (
            "back",
            "go back",
            "menu",
            "home",
        ):
            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

        if command in (
            "2",
            "search",
            "search food",
        ):
            from users.constants import SEARCH_RESTAURANTS

            StateService.set(
                conversation,
                SEARCH_RESTAURANTS,
                push=True,
            )
            WhatsAppService.send_text(
                phone,
                "🔎 Type the food or restaurant name." + NAVIGATION,
            )
            return

        if command in (
            "3",
            "browse",
            "browse menu",
            "browse restaurants",
        ):
            from .restaurant import RestaurantHandler

            return RestaurantHandler().handle(
                phone,
                "",
            )

        matches, warning = self._match_order(
            customer,
            conversation,
            message,
        )

        if not matches:
            WhatsAppService.send_buttons(
                phone,
                """I couldn't confidently match that to menu items near you.

Try using exact meal names from a restaurant menu, or search/browse first.""",
                [
                    ("2", "Search Food"),
                    ("3", "Browse Menu"),
                    ("back", "Go Back"),
                ],
                "You can also reply 2, 3, or back.",
            )
            return

        restaurant = matches[0]["item"].restaurant

        conversation.search_result_ids = [
            {
                "menu_item_id": match["item"].id,
                "quantity": match["quantity"],
            }
            for match in matches
        ]
        conversation.search_result_type = [
            "typed_order_pending",
        ]
        conversation.save(
            update_fields=[
                "search_result_ids",
                "search_result_type",
                "updated_at",
            ]
        )

        StateService.set_restaurant(
            conversation,
            restaurant,
        )
        StateService.set(
            conversation,
            CONFIRM_TYPED_ORDER,
            push=True,
        )

        text = f"🧾 *Confirm Order*\n\n🏪 {restaurant.name}\n\n"
        subtotal = 0

        for index, match in enumerate(
            matches,
            start=1,
        ):
            item = match["item"]
            quantity = match["quantity"]
            line_total = item.price * quantity
            subtotal += line_total
            text += (
                f"{index}. {quantity} x *{item.name}*\n"
                f"   {money(item.price)} each · {money(line_total)}\n"
            )

        text += f"\nFood subtotal: *{money(subtotal)}*"

        if warning:
            text += f"\n\nNote: {warning}"

        text += "\n\nContinue to add this to your cart, or type again."

        WhatsAppService.send_buttons(
            phone,
            text,
            [
                ("1", "Continue"),
                ("2", "Type Again"),
                ("back", "Go Back"),
            ],
            "You can also reply 1, 2, or back.",
        )

    def _handle_confirmation(
        self,
        phone,
        customer,
        conversation,
        command,
    ):

        if command in (
            "2",
            "type again",
            "retry",
        ):
            return self.start(
                phone,
                customer,
                conversation,
            )

        if command in (
            "back",
            "go back",
            "menu",
            "home",
        ):
            return HomeHandler.show(
                phone,
                customer,
                conversation,
            )

        if command not in (
            "1",
            "continue",
            "yes",
            "confirm",
            "add",
            "add to cart",
        ):
            WhatsAppService.send_text(
                phone,
                "Reply 1 to continue, 2 to type again, or back."
                + NAVIGATION,
            )
            return

        pending = conversation.search_result_ids or []

        if not pending:
            return self.start(
                phone,
                customer,
                conversation,
            )

        try:
            for entry in pending:
                item = MenuItem.objects.get(
                    id=entry["menu_item_id"],
                    is_available=True,
                )
                CartService.add_item(
                    customer,
                    item,
                    quantity=max(
                        int(entry.get("quantity", 1)),
                        1,
                    ),
                )
        except (MenuItem.DoesNotExist, ValueError) as exc:
            WhatsAppService.send_text(
                phone,
                f"{exc}\n\nType clear cart to start a new order."
                + NAVIGATION,
            )
            return

        conversation.search_result_ids = []
        conversation.search_result_type = []
        conversation.save(
            update_fields=[
                "search_result_ids",
                "search_result_type",
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

    def _match_order(
        self,
        customer,
        conversation,
        message,
    ):

        normalized_message = self._normalize(message)

        if not normalized_message:
            return [], ""

        restaurants = SearchService._restaurant_scope(
            customer,
        )

        items = (
            MenuItem.objects.filter(
                restaurant__in=restaurants,
                is_available=True,
            )
            .filter(
                Q(inventory__quantity__gt=0)
                |
                Q(inventory__isnull=True)
            )
            .select_related(
                "restaurant",
                "category",
                "inventory",
            )
            .order_by(
                "-restaurant__rating",
                "restaurant__name",
                "name",
            )
        )

        if conversation.selected_restaurant_id:
            scoped = items.filter(
                restaurant=conversation.selected_restaurant,
            )
            if scoped.exists():
                items = scoped

        candidates = []

        for item in items:
            match = self._match_item(
                item,
                normalized_message,
            )

            if not match:
                continue

            candidates.append(
                {
                    "item": item,
                    "quantity": self._safe_quantity(
                        item,
                        match["quantity"],
                    ),
                    "score": match["score"],
                }
            )

        if not candidates:
            return [], ""

        groups = defaultdict(list)

        for candidate in candidates:
            groups[candidate["item"].restaurant_id].append(candidate)

        best_group = sorted(
            groups.values(),
            key=lambda group: (
                len(group),
                sum(candidate["score"] for candidate in group),
                group[0]["item"].restaurant.rating,
            ),
            reverse=True,
        )[0]

        warning = ""

        if len(groups) > 1:
            warning = (
                "I matched the clearest single-restaurant order so your cart "
                "stays checkout-ready."
            )

        return best_group[:10], warning

    def _match_item(
        self,
        item,
        normalized_message,
    ):

        item_name = self._normalize(item.name)
        tokens = [
            token
            for token in item_name.split()
            if len(token) > 2
        ]

        exact_quantity = self._quantity_before_phrase(
            normalized_message,
            item_name,
        )

        if exact_quantity is not None:
            return {
                "quantity": exact_quantity,
                "score": len(tokens) + 3,
            }

        if not tokens:
            return None

        if all(
            re.search(
                rf"\b{re.escape(token)}\b",
                normalized_message,
            )
            for token in tokens
        ):
            return {
                "quantity": self._quantity_before_phrase(
                    normalized_message,
                    tokens[0],
                )
                or 1,
                "score": len(tokens),
            }

        return None

    def _quantity_before_phrase(
        self,
        normalized_message,
        phrase,
    ):

        units = "|".join(self.UNIT_WORDS)
        number_words = "|".join(self.QUANTITY_WORDS.keys())
        pattern = (
            rf"(?:\b(?P<number>\d+|{number_words})\b\s*)?"
            rf"(?:(?:{units})\s*)*"
            rf"\b{re.escape(phrase)}(?:s|es)?\b"
        )

        match = re.search(
            pattern,
            normalized_message,
        )

        if not match:
            return None

        number = match.group("number")

        if not number:
            return 1

        if number.isdigit():
            return max(
                int(number),
                1,
            )

        return self.QUANTITY_WORDS.get(
            number,
            1,
        )

    @staticmethod
    def _safe_quantity(
        item,
        quantity,
    ):

        quantity = max(
            int(quantity or 1),
            1,
        )

        if hasattr(item, "inventory"):
            return min(
                quantity,
                max(item.inventory.quantity, 1),
            )

        return quantity

    @staticmethod
    def _normalize(value):

        value = value.lower()
        value = value.replace("jellof", "jollof")
        value = value.replace("sharwama", "shawarma")
        value = value.replace("coca cola", "coke")
        value = re.sub(
            r"[^a-z0-9\s]",
            " ",
            value,
        )
        return re.sub(
            r"\s+",
            " ",
            value,
        ).strip()
