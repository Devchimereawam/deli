from django.db.models import Prefetch, Q

from restaurants.models import (
    Restaurant,
    MenuItem,
    Category,
    OpeningHour,
)
from datetime import datetime

class RestaurantService:

    @staticmethod
    def _base_queryset():

        return (
            Restaurant.objects.filter(
                is_active=True,
            )
            .prefetch_related(
                Prefetch(
                    "categories",
                    queryset=Category.objects.order_by("name"),
                ),
                Prefetch(
                    "menu_items",
                    queryset=MenuItem.objects.filter(
                        is_available=True,
                    )
                    .select_related(
                        "category",
                    )
                    .order_by(
                        "category__name",
                        "name",
                    ),
                ),
                Prefetch(
                    "opening_hours",
                    queryset=OpeningHour.objects.order_by("id"),
                ),
            )
        )

    @classmethod
    def nearby_restaurants(cls, customer):

        address = customer.default_address

        if not address:
            return Restaurant.objects.none()

        queryset = cls._base_queryset()

        # ---------------------------------
        # 1. Same Area
        # ---------------------------------

        if address.area:

            restaurants = queryset.filter(
                area=address.area,
            )

            if restaurants.exists():

                return restaurants.order_by(
                    "-rating",
                    "name",
                    "id",
                )

        # ---------------------------------
        # 2. Same City
        # ---------------------------------

        if address.city:

            restaurants = queryset.filter(
                area__city=address.city,
            )

            if restaurants.exists():

                return restaurants.order_by(
                    "-rating",
                    "name",
                    "id",
                )

        # ---------------------------------
        # 3. Same State
        # ---------------------------------

        if address.state:

            restaurants = queryset.filter(
                area__city__state=address.state,
            )

            if restaurants.exists():

                return restaurants.order_by(
                    "-rating",
                    "name",
                    "id",
                )

        return Restaurant.objects.none()

    @staticmethod
    def get_restaurant(pk):

        return (
            Restaurant.objects.prefetch_related(
                "categories",
                "menu_items",
                "opening_hours",
            )
            .get(
                pk=pk,
                is_active=True,
            )
        )

    @staticmethod
    def format_opening_hours(restaurant):

        day_map = {
            0: "MON",
            1: "TUE",
            2: "WED",
            3: "THU",
            4: "FRI",
            5: "SAT",
            6: "SUN",
        }

        today = day_map[datetime.today().weekday()]

        hours = (
            restaurant.opening_hours
            .filter(day=today)
            .first()
        )

        if not hours:
            return "Opening hours unavailable"

        if hours.is_closed:
            return "Closed today"

        return (
            f"Open "
            f"{hours.opening_time.strftime('%I:%M %p')} - "
            f"{hours.closing_time.strftime('%I:%M %p')}"
        )

    @staticmethod
    def get_menu_item(pk):

        return (
            MenuItem.objects.select_related(
                "restaurant",
                "category",
            ).get(
                pk=pk,
                is_available=True,
            )
        )