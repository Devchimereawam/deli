from django.db.models import Q

from restaurants.models import Restaurant, MenuItem


class SearchService:

    @staticmethod
    def _restaurant_scope(customer):

        address = customer.default_address

        if not address:
            return Restaurant.objects.none()

        queryset = Restaurant.objects.filter(
            is_active=True,
        )

        if address.area:
            area_matches = queryset.filter(
                area=address.area,
            )

            if area_matches.exists():
                return area_matches

        if address.city:
            city_matches = queryset.filter(
                area__city=address.city,
            )

            if city_matches.exists():
                return city_matches

        if address.state:
            state_matches = queryset.filter(
                area__city__state=address.state,
            )

            if state_matches.exists():
                return state_matches

        return Restaurant.objects.none()

    @staticmethod
    def search_food(customer, query):

        restaurants = SearchService._restaurant_scope(
            customer,
        )

        return (
            MenuItem.objects.filter(
                restaurant__in=restaurants,
                is_available=True,
            )
            .filter(
                Q(name__icontains=query)
                |
                Q(category__name__icontains=query)
                |
                Q(restaurant__name__icontains=query)
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

        scoped_restaurants = cls._restaurant_scope(
            customer,
        )

        restaurants = (
            scoped_restaurants
            .filter(
                Q(name__icontains=query)
                |
                Q(description__icontains=query)
                |
                Q(cuisine_type__icontains=query)
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
