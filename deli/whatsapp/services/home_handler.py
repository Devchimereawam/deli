from users.constants import HOME
from restaurants.models import MenuItem

from whatsapp.constants import NAVIGATION

from .state_service import StateService
from .customer_service import CustomerService
from .formatting import money
from .whatsapp_service import WhatsAppService


class HomeHandler:

    @classmethod
    def show(
        cls,
        phone,
        customer,
        conversation,
    ):

        StateService.reset(
            conversation,
            HOME,
        )

        hot_meals = []

        address = customer.default_address

        if address:
            meal_scope = MenuItem.objects.filter(
                restaurant__is_active=True,
                is_available=True,
            )

            if address.area and meal_scope.filter(
                restaurant__area=address.area,
            ).exists():
                meal_scope = meal_scope.filter(
                    restaurant__area=address.area,
                )
            elif address.city and meal_scope.filter(
                restaurant__area__city=address.city,
            ).exists():
                meal_scope = meal_scope.filter(
                    restaurant__area__city=address.city,
                )
            else:
                meal_scope = MenuItem.objects.none()

            hot_meals = list(
                meal_scope.select_related(
                    "restaurant",
                ).order_by(
                    "-is_featured",
                    "-restaurant__rating",
                    "price",
                    "name",
                )[:3]
            )

        hot_text = ""

        if hot_meals:
            hot_text = "🔥 *Hot Meals Near You*\n"

            for index, item in enumerate(
                hot_meals,
                start=1,
            ):
                hot_text += (
                    f"{index}. *{item.name}* - {money(item.price)}\n"
                    f"   ⭐ ({item.rating}) ({item.total_reviews}) · {item.restaurant.name}\n"
                )

            hot_text += "\n"

        WhatsAppService.send_list(
            phone,
            f"""🍽️ *Deli*

{
f"Welcome back, *{customer.name}*."
if customer.name
else "Welcome. Easy buy any food or see food options near you with Deli."
}

{
f"📍 Delivering around: {CustomerService.customer_location(customer)}"
if customer.default_address
else ""
}

Stop asking or going out just to see what they have. View real-time menus and order from home.

────────────

{hot_text}
────────────

😋 *What are you craving today?*

1️⃣ Type Order

2️⃣ Browse Restaurants

3️⃣ Search Food

4️⃣ My Orders

5️⃣ Change Location
""" + NAVIGATION,
            [
                ("1", "Type Order", "Write everything in one message"),
                ("2", "Restaurants", "See restaurants near you"),
                ("3", "Search Food", "Find meals or restaurants"),
                ("4", "My Orders", "Track recent orders"),
                ("5", "Change Location", "Update delivery area"),
            ],
            "Open menu",
            "You can also reply 1, 2, 3, 4, or 5.",
)
