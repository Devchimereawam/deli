from users.constants import HOME

from whatsapp.constants import NAVIGATION

from .state_service import StateService
from .customer_service import CustomerService
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
        
        WhatsAppService.send_text(
            phone,
            f"""🏠 *Home*

{
f"Welcome back to Deli 🍽️ *{customer.name}*"
if customer.name
else "Welcome to Deli 🍽️"
}

{
f"📍 {CustomerService.customer_location(customer)}"
if customer.default_address
else ""
}

😋 What are you craving today?

1️⃣ Browse Restaurants

2️⃣ Search Food

3️⃣ My Orders

4️⃣ Change Location
""" + NAVIGATION
)