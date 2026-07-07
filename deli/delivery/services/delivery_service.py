from decimal import Decimal

from delivery.models import DeliveryRider


class DeliveryService:

    DELI_DASH_NAME = "Deli Dash Standard"
    DELI_DASH_EXPRESS_NAME = "Deli Dash Express"
    DELI_DASH_FEE = Decimal("1800.00")
    DELI_DASH_EXPRESS_FEE = Decimal("2400.00")

    # Backwards-compatible aliases for existing code paths and migrations.
    DELISEND_NAME = DELI_DASH_NAME
    DELISEND_FEE = DELI_DASH_FEE
    DELISEND_EXPRESS_FEE = DELI_DASH_EXPRESS_FEE

    @classmethod
    def riders_for_customer(cls, customer):

        address = customer.default_address

        queryset = DeliveryRider.objects.filter(
            is_active=True,
            is_available=True,
        )

        if address and address.area:
            area_matches = queryset.filter(
                area=address.area,
            )

            if area_matches.exists():
                return area_matches.order_by(
                    "-rating",
                    "base_fee",
                    "name",
                )

        return queryset.order_by(
            "-rating",
            "base_fee",
            "name",
        )

    @classmethod
    def rider_options(cls, customer):

        riders = list(
            cls.riders_for_customer(customer)[:10]
        )

        options = [
            {
                "kind": "rider",
                "id": rider.id,
                "name": rider.name,
                "fee": rider.base_fee,
                "rating": rider.rating,
                "reviews": rider.total_reviews,
                "vehicle": rider.vehicle_type,
            }
            for rider in riders
        ]

        options.extend(
            [
                {
                    "kind": "deli_dash",
                    "id": None,
                    "name": cls.DELI_DASH_NAME,
                    "fee": cls.DELI_DASH_FEE,
                    "rating": Decimal("5.00"),
                    "reviews": 0,
                    "vehicle": "Deli delivery",
                },
                {
                    "kind": "deli_dash",
                    "id": None,
                    "name": cls.DELI_DASH_EXPRESS_NAME,
                    "fee": cls.DELI_DASH_EXPRESS_FEE,
                    "rating": Decimal("5.00"),
                    "reviews": 0,
                    "vehicle": "Priority Deli delivery",
                },
            ]
        )

        return options

    @classmethod
    def delisend_delta(cls, selected_fee):

        delta = cls.DELI_DASH_FEE - selected_fee

        if delta > 0:
            return f"an extra ₦{delta}"

        if delta < 0:
            return f"₦{abs(delta)} less"

        return "no extra charge"
