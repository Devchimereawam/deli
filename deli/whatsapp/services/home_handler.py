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
        best_restaurants = []

        address = customer.default_address

        if address and address.area:
            hot_meals = list(
                MenuItem.objects.filter(
                    restaurant__area=address.area,
                    restaurant__is_active=True,
                    is_available=True,
                )
                .select_related(
                    "restaurant",
                )
                .order_by(
                    "-is_featured",
                    "-restaurant__rating",
                    "price",
                    "name",
                )[:3]
            )

            best_restaurants = list(
                address.area.restaurants.filter(
                    is_active=True,
                ).order_by(
                    "-rating",
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

        best_text = ""

        if best_restaurants:
            best_text = "⭐ *Best Rated Restaurants*\n"

            for index, restaurant in enumerate(
                best_restaurants,
                start=1,
            ):
                best_text += (
                    f"{index}. {restaurant.name}\n"
                    f"   ⭐ ({restaurant.rating}) ({restaurant.total_reviews})\n"
                )

            best_text += "\n"
        
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

{hot_text}{best_text}
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
