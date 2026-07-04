from users.constants import HOME
from .navigation_service import NavigationService

class StateService:
    """
    Centralized service for managing conversation state.

    Every screen transition should go through this service.
    """

    @staticmethod
    def get(conversation):

        return conversation.current_step

    @staticmethod
    def set(
        conversation,
        step,
        push=False,
    ):

        conversation.current_step = step

        conversation.save(
            update_fields=[
                "current_step",
                "updated_at",
            ]
        )

        if push:
            NavigationService.push(
                conversation,
                step,
            )

        return conversation
    
    @staticmethod
    def go_to(
        conversation,
        step,
    ):

        return StateService.set(
            conversation,
            step,
            push=True,
        )

    @staticmethod
    def clear_selection(
        conversation,
    ):

        conversation.selected_restaurant = None
        conversation.selected_category = None
        conversation.selected_menu_item = None

        conversation.save(
            update_fields=[
                "selected_restaurant",
                "selected_category",
                "selected_menu_item",
                "updated_at",
            ]
        )

    @staticmethod
    def reset(
        conversation,
        step,
    ):

        conversation.current_step = step
        conversation.selected_restaurant = None
        conversation.selected_category = None
        conversation.selected_menu_item = None
        conversation.search_query = ""

        if step == HOME:

            NavigationService.reset(
                conversation,
            )

        conversation.save(
            update_fields=[
                "current_step",
                "selected_restaurant",
                "selected_category",
                "selected_menu_item",
                "search_query",
                "updated_at",
            ]
        )

        return conversation

    @staticmethod
    def set_restaurant(
        conversation,
        restaurant,
    ):

        conversation.selected_restaurant = restaurant
        conversation.selected_category = None
        conversation.selected_menu_item = None

        conversation.save(
            update_fields=[
                "selected_restaurant",
                "selected_category",
                "selected_menu_item",
                "updated_at",
            ]
        )

    @staticmethod
    def set_category(
        conversation,
        category,
    ):

        conversation.selected_category = category
        conversation.selected_menu_item = None

        conversation.save(
            update_fields=[
                "selected_category",
                "selected_menu_item",
                "updated_at",
            ]
        )

    @staticmethod
    def set_menu_item(
        conversation,
        item,
    ):

        conversation.selected_menu_item = item

        conversation.save(
            update_fields=[
                "selected_menu_item",
                "updated_at",
            ]
        )

    @staticmethod
    def set_search(
        conversation,
        query,
    ):

        conversation.search_query = query

        conversation.save(
            update_fields=[
                "search_query",
                "updated_at",
            ]
        )
        
    @staticmethod
    def set_search_results(
        conversation,
        ids,
    ):

        conversation.search_result_ids = ids

        conversation.save(
            update_fields=[
                "search_result_ids",
                "updated_at",
            ]
        )
        
    @staticmethod
    def set_restaurant_list(
        conversation,
        ids,
    ):

        conversation.restaurant_ids = ids or []

        conversation.save(
            update_fields=[
                "restaurant_ids",
                "updated_at",
            ]
        )