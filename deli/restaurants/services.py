from django.db.models import Prefetch, Q 
from .models import (
    Restaurant,
    MenuItem,
)


class RestaurantService:

    @staticmethod
    def nearby(area):

        return (
            Restaurant.objects
            .filter(
                area=area,
                is_active=True,
            )
            .order_by(
                "-rating",
                "-is_verified",
                "name",
            )
        )

    @staticmethod
    def by_slug(slug):

        return (
            Restaurant.objects
            .prefetch_related(
                Prefetch(
                    "menu_items",
                    queryset=MenuItem.objects.filter(
                        is_available=True,
                    ).select_related(
                        "category",
                        "inventory",
                    ),
                )
            )
            .get(
                slug=slug,
            )
        )

    @staticmethod
    def search(area, query):

        return (
            Restaurant.objects.filter(
                area=area,
                is_active=True,
            ).filter(
                Q(name__icontains=query)
                |
                Q(menu_items__name__icontains=query)
                |
                Q(menu_items__category__name__icontains=query)
            ).distinct()
            .distinct()
            .order_by(
                "-rating",
                "name",
            )
        )
    @staticmethod
    def nearby_restaurants(customer):
        """
        Wrapper used by the WhatsApp flow.
        """
        if not customer.default_address:
            return Restaurant.objects.none()

        return RestaurantService.nearby(
            customer.default_address.area
        )


    @staticmethod
    def format_opening_hours(restaurant):
        """
        Safe formatter that matches the OpeningHours model.
        """

        from datetime import datetime

        today = datetime.today().weekday()

        hours = (
            restaurant.opening_hours
            .filter(day=today)   # <-- NOT day_of_week
            .first()
        )

        if not hours:
            return "Hours unavailable"

        if hours.is_closed:
            return "Closed today"

        return (
            f"{hours.opening_time.strftime('%I:%M %p')} - "
            f"{hours.closing_time.strftime('%I:%M %p')}"
        )