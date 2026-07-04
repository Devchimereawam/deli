from decimal import Decimal
from uuid import uuid4

from django.db import transaction

from cart.services.cart_service import CartService

from ..models import (
    Order,
    OrderItem,
)


class OrderService:

    DELIVERY_FEE = Decimal("1000.00")

    @classmethod
    @transaction.atomic
    def create_order(
        cls,
        customer,
    ):

        summary = CartService.cart_summary(
            customer,
        )

        items = list(
            summary["items"]
        )

        if not items:

            return None

        restaurant = (
            items[0]
            .menu_item
            .restaurant
        )

        order = Order.objects.create(
            customer=customer,
            restaurant=restaurant,
            subtotal=summary["subtotal"],
            delivery_fee=summary["delivery_fee"],
            total=summary["total"],
            checkout_reference=f"ORD-{uuid4().hex.upper()}",
            status=Order.STATUS_PENDING,
        )

        order_items = []

        for item in items:

            order_items.append(

                OrderItem(

                    order=order,

                    menu_item=item.menu_item,

                    name=item.menu_item.name,

                    quantity=item.quantity,

                    unit_price=item.unit_price,

                    subtotal=item.subtotal,

                )

            )

        OrderItem.objects.bulk_create(
            order_items,
        )

        return order

    @classmethod
    @transaction.atomic
    def checkout(
        cls,
        customer,
    ):

        order = cls.create_order(
            customer,
        )

        if order is None:

            return None

        CartService.clear_cart(
            customer,
        )

        return order

    @staticmethod
    def mark_payment_pending(
        order,
        checkout_url,
        payment_reference,
    ):

        order.checkout_url = checkout_url

        order.payment_reference = (
            payment_reference
        )

        order.status = (
            Order.STATUS_AWAITING_PAYMENT
        )

        order.save(
            update_fields=[
                "checkout_url",
                "payment_reference",
                "status",
                "updated_at",
            ]
        )

        return order

    @staticmethod
    def mark_paid(
        order,
    ):

        order.status = (
            Order.STATUS_PAID
        )

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return order

    @staticmethod
    def mark_cancelled(
        order,
    ):

        order.status = (
            Order.STATUS_CANCELLED
        )

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        return order