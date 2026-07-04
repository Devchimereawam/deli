from django.db.models import Q

from restaurants.models import Restaurant, MenuItem

from .restaurant_service import RestaurantService


class SearchService:
    
    @staticmethod
    def search_food(customer, query):

        return (
            MenuItem.objects.filter(
                restaurant__is_active=True,
                is_available=True,
            )
            .filter(
                Q(name__istartswith=query)
                |
                Q(category__name__istartswith=query)
            )
            .select_related(
                "restaurant",
                "category",
            )
            .order_by(
                "-restaurant__rating",
                "restaurant__name",
                "category__name",
                "name",
            )
        )

    @classmethod
    def search(cls, customer, query):

        restaurants = (
            Restaurant.objects.filter(
                is_active=True,
            )
            .filter(
                Q(name__icontains=query)
                |
                Q(description__icontains=query)
            )
            .order_by(
                "-rating",
                "name",
            )
        )

        menu_items = cls.search_food(
            customer,
            query,
        )

        return restaurants, menu_items