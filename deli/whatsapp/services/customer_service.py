from users.models import (
    Customer,
    ConversationState,
)


class CustomerService:

    @staticmethod
    def get_customer(phone):

        customer, created = Customer.objects.get_or_create(
            phone=phone,
        )

        conversation, _ = (
            ConversationState.objects.get_or_create(
                customer=customer,
            )
        )

        return customer, conversation, created

    @staticmethod
    def customer_location(customer):

        address = customer.default_address

        if not address:
            return "Unknown"

        return address.display_location

    @staticmethod
    def save_name(customer, name):

        customer.name = name.strip()

        customer.is_registered = True

        customer.save()

        return customer

    @staticmethod
    def select_restaurant(
        conversation,
        restaurant,
    ):

        conversation.selected_restaurant = restaurant
        conversation.selected_category = None
        conversation.selected_menu_item = None
        conversation.save()

    @staticmethod
    def select_category(
        conversation,
        category,
    ):

        conversation.selected_category = category
        conversation.selected_menu_item = None
        conversation.save()

    @staticmethod
    def select_menu_item(
        conversation,
        menu_item,
    ):

        conversation.selected_menu_item = menu_item
        conversation.save()

    @staticmethod
    def clear_restaurant_state(
        conversation,
    ):

        conversation.selected_restaurant = None
        conversation.selected_category = None
        conversation.selected_menu_item = None
        conversation.save()