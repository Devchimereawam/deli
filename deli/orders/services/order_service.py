from decimal import Decimal
from datetime import timedelta
from uuid import uuid4

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from cart.services.cart_service import CartService
from delivery.services import DeliveryService
from whatsapp.services.formatting import money

from ..models import (
    Order,
    OrderItem,
)


class OrderService:

    PROVIDER_TIMEOUT_MINUTES = 5

    @classmethod
    @transaction.atomic
    def create_order(
        cls,
        customer,
        delivery_address="",
        delivery_contact_phone="",
        delivery_notes="",
        delivery_rider=None,
        delivery_fee=None,
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

        if any(item.menu_item.restaurant_id != restaurant.id for item in items):
            raise ValueError(
                "Please order from one restaurant at a time."
            )

        fee = (
            delivery_fee
            if delivery_fee is not None
            else summary["delivery_fee"]
        )

        customer_service_fee = settings.DELI_CUSTOMER_SERVICE_FEE
        maintenance_fee = settings.DELI_MAINTENANCE_FEE
        restaurant_platform_fee = settings.DELI_RESTAURANT_PAYOUT_FEE
        rider_platform_fee = settings.DELI_RIDER_PAYOUT_FEE

        total = (
            summary["subtotal"]
            + fee
            + customer_service_fee
            + maintenance_fee
        )

        order = Order.objects.create(
            customer=customer,
            restaurant=restaurant,
            subtotal=summary["subtotal"],
            delivery_fee=fee,
            customer_service_fee=customer_service_fee,
            maintenance_fee=maintenance_fee,
            restaurant_platform_fee=restaurant_platform_fee,
            rider_platform_fee=rider_platform_fee,
            delivery_rider=delivery_rider,
            delivery_address=delivery_address,
            delivery_contact_phone=delivery_contact_phone,
            delivery_notes=delivery_notes,
            total=total,
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

                    unit_price=item.menu_item.price,

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
        delivery_address="",
        delivery_contact_phone="",
        delivery_notes="",
        delivery_rider=None,
        delivery_fee=None,
    ):

        order = cls.create_order(
            customer,
            delivery_address=delivery_address,
            delivery_contact_phone=delivery_contact_phone,
            delivery_notes=delivery_notes,
            delivery_rider=delivery_rider,
            delivery_fee=delivery_fee,
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

    @classmethod
    @transaction.atomic
    def mark_paid(
        cls,
        order,
    ):

        order = Order.objects.select_for_update().get(
            id=order.id,
        )
        order.status = (
            Order.STATUS_PAID
        )
        update_fields = [
            "status",
            "updated_at",
        ]

        if not order.inventory_deducted_at:
            cls._deduct_inventory(order)
            order.inventory_deducted_at = timezone.now()
            update_fields.append("inventory_deducted_at")

        order.save(
            update_fields=update_fields,
        )

        cls.notify_deli_admin_settlement_preview(order)
        cls.clear_other_awaiting_payment_orders(order)

        return order

    @staticmethod
    def clear_other_awaiting_payment_orders(order):

        Order.objects.filter(
            customer=order.customer,
            status=Order.STATUS_AWAITING_PAYMENT,
        ).exclude(
            id=order.id,
        ).update(
            status=Order.STATUS_CANCELLED,
            updated_at=timezone.now(),
        )

    @staticmethod
    def notify_customer_payment_confirmed(order):

        from users.constants import ORDER_STATUS
        from users.models import ConversationState
        from whatsapp.services.state_service import StateService
        from whatsapp.services.whatsapp_service import WhatsAppService

        conversation, _ = ConversationState.objects.get_or_create(
            customer=order.customer,
        )
        StateService.set_order(
            conversation,
            order,
        )
        StateService.set(
            conversation,
            ORDER_STATUS,
        )

        WhatsAppService.send_list(
            order.customer.phone,
            f"""✅ *Payment successful*

Your food is on its way.

Your rider will contact you when they get to your address.

Thanks for using Deli.

{OrderService.order_tracking_text(order)}""",
            OrderService.post_payment_action_rows(),
            "Order actions",
            "You can also reply 1, 2, 3, 4, 5, or 6.",
        )

    @staticmethod
    def post_payment_action_rows():

        return [
            (
                "track_order",
                "Track Order",
                "See the current delivery stage",
            ),
            (
                "confirm_delivered",
                "Confirm Delivered",
                "Tell us the meal has arrived",
            ),
            (
                "review",
                "Review",
                "Rate the meal or restaurant",
            ),
            (
                "end_session",
                "End Session",
                "Close this chat flow",
            ),
            (
                "home",
                "Keep Shopping",
                "Back to the main menu",
            ),
            (
                "remove_order",
                "Remove Order",
                "Delete unpaid or cancelled order",
            ),
        ]

    @staticmethod
    def order_tracking_text(order):

        order.refresh_from_db()

        restaurant_ready = order.status in (
            Order.STATUS_ACCEPTED,
            Order.STATUS_PREPARING,
            Order.STATUS_ON_THE_WAY,
            Order.STATUS_DELIVERED,
        )
        picked_up = order.status in (
            Order.STATUS_ON_THE_WAY,
            Order.STATUS_DELIVERED,
        )
        on_the_way = order.status in (
            Order.STATUS_ON_THE_WAY,
            Order.STATUS_DELIVERED,
        )

        if order.status == Order.STATUS_PAID:
            current = "Payment confirmed. We are confirming the restaurant and rider."
        elif order.status in (
            Order.STATUS_ACCEPTED,
            Order.STATUS_PREPARING,
        ):
            current = "Ready at restaurant."
        elif order.status == Order.STATUS_ON_THE_WAY:
            current = "Picked up and on the way to you."
        elif order.status == Order.STATUS_DELIVERED:
            current = "Delivered."
        elif order.status == Order.STATUS_AWAITING_PAYMENT:
            current = "Awaiting payment confirmation."
        else:
            current = order.get_status_display()

        def mark(done):
            return "Done" if done else "Waiting"

        return f"""📦 *Order:* {order.checkout_reference}
🏪 *Restaurant:* {order.restaurant.name}
🚚 *Rider:* {order.delivery_rider.name if order.delivery_rider else DeliveryService.DELI_DASH_NAME}

*Current:* {current}

1. Ready at restaurant: {mark(restaurant_ready)}
2. Picked up: {mark(picked_up)}
3. On your way to you: {mark(on_the_way)}"""

    @staticmethod
    def _deduct_inventory(order):

        from restaurants.models import Inventory

        items = order.items.select_related(
            "menu_item",
        )

        for order_item in items:
            inventory = (
                Inventory.objects
                .select_for_update()
                .filter(
                    menu_item=order_item.menu_item,
                )
                .first()
            )

            if not inventory:
                continue

            inventory.quantity = max(
                inventory.quantity - order_item.quantity,
                0,
            )
            inventory.save(
                update_fields=[
                    "quantity",
                    "updated_at",
                ]
            )

            if inventory.quantity == 0:
                order_item.menu_item.is_available = False
                order_item.menu_item.save(
                    update_fields=[
                        "is_available",
                    ]
                )

    @staticmethod
    def mark_delivered(
        order,
    ):

        order.status = Order.STATUS_DELIVERED
        order.review_requested_at = timezone.now()

        order.save(
            update_fields=[
                "status",
                "review_requested_at",
                "updated_at",
            ]
        )

        from users.constants import REVIEW_CHOICE
        from users.models import ConversationState
        from whatsapp.services.state_service import StateService
        from whatsapp.services.whatsapp_service import WhatsAppService

        conversation, _ = ConversationState.objects.get_or_create(
            customer=order.customer,
        )
        StateService.set_order(conversation, order)
        StateService.set(conversation, REVIEW_CHOICE)

        WhatsAppService.send_buttons(
            order.customer.phone,
            f"""✅ Your order *{order.checkout_reference}* has been delivered.

Thanks for your patronage. Can't wait to have you back.

20,000 more customers using Deli review meals and restaurants so people like you can find tasty dishes faster.

Don't forget to review the restaurant or food after eating.

Choose what to review now, or type review later.""",
            [
                ("1", "Review Meal"),
                ("2", "Restaurant"),
            ],
            "You can also reply 1 or 2.",
        )

        OrderService.notify_deli_admin_payout_ready(order)

        return order

    @staticmethod
    def restaurant_net_payout(order):

        return max(
            order.subtotal - order.restaurant_platform_fee,
            Decimal("0.00"),
        )

    @staticmethod
    def rider_net_payout(order):

        if not order.delivery_rider:
            return Decimal("0.00")

        return max(
            order.delivery_fee - order.rider_platform_fee,
            Decimal("0.00"),
        )

    @classmethod
    def notify_deli_admin_settlement_preview(cls, order):

        cls._notify_deli_admin_payout(
            order,
            title="Payment received - payout preview",
            ready=False,
        )

    @classmethod
    def notify_deli_admin_payout_ready(cls, order):

        cls._notify_deli_admin_payout(
            order,
            title="Order delivered - payout ready",
            ready=True,
        )

    @classmethod
    def _notify_deli_admin_payout(
        cls,
        order,
        title,
        ready,
    ):

        ops_number = getattr(
            settings,
            "DELI_DASH_WHATSAPP_NUMBER",
            "",
        )

        if not ops_number:
            return

        from whatsapp.services.whatsapp_service import WhatsAppService

        restaurant_net = cls.restaurant_net_payout(order)
        rider_net = cls.rider_net_payout(order)
        command = (
            f"pipenv run python manage.py payout_delivered_orders --order {order.checkout_reference} --execute"
            if ready
            else f"pipenv run python manage.py payout_delivered_orders --order {order.checkout_reference}"
        )

        rider_text = (
            f"""
Rider:
{order.delivery_rider.name}
Gross delivery: {money(order.delivery_fee)}
Deli rider fee: {money(order.rider_platform_fee)}
Net rider payout: {money(rider_net)}
Bank: {order.delivery_rider.bank_name or "Not set"} {order.delivery_rider.account_number or ""}
Account name: {order.delivery_rider.account_name or "Not set"}"""
            if order.delivery_rider
            else "\nRider: Deli Dash internal delivery, no external rider payout."
        )

        WhatsAppService.send_text(
            ops_number,
            f"""💼 *{title}*

Order: *{order.checkout_reference}*
Customer: {order.customer.name or order.customer.phone}
Restaurant: {order.restaurant.name}

Customer paid:
Food: {money(order.subtotal)}
Delivery: {money(order.delivery_fee)}
Deli customer fee: {money(order.customer_service_fee)}
Maintenance fee: {money(order.maintenance_fee)}
Total: {money(order.total)}

Restaurant payout:
Gross food: {money(order.subtotal)}
Deli restaurant fee: {money(order.restaurant_platform_fee)}
Net restaurant payout: {money(restaurant_net)}
Bank: {order.restaurant.bank_name or "Not set"} {order.restaurant.account_number or ""}
Account name: {order.restaurant.account_name or "Not set"}
{rider_text}

Command:
{command}

{"Run this only after delivery is complete." if not ready else "This order is delivered. Run --execute only when ready to send money."}"""
        )

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

    @staticmethod
    def order_items_text(order):

        return "\n".join(
            f"- {item.quantity} x {item.name} ({money(item.subtotal)})"
            for item in order.items.all()
        )

    @classmethod
    def ask_providers_availability(
        cls,
        order,
    ):

        now = timezone.now()

        if order.restaurant.send_orders_to_deli_dash:
            order.restaurant_availability_status = Order.PROVIDER_ACCEPTED
            order.restaurant_asked_at = now
        else:
            order.restaurant_availability_status = Order.PROVIDER_ASKED
            order.restaurant_asked_at = now

        if order.delivery_rider:
            order.rider_availability_status = Order.PROVIDER_ASKED
            order.rider_asked_at = now
        else:
            order.rider_availability_status = Order.PROVIDER_ACCEPTED
            order.fallback_status = Order.FALLBACK_ACCEPTED

        order.save(
            update_fields=[
                "restaurant_availability_status",
                "rider_availability_status",
                "restaurant_asked_at",
                "rider_asked_at",
                "fallback_status",
                "updated_at",
            ]
        )

        from whatsapp.services.whatsapp_service import WhatsAppService

        if order.restaurant.send_orders_to_deli_dash:
            cls.send_restaurant_order(order)

            WhatsAppService.send_text(
                order.customer.phone,
                f"""Heads up: *{order.restaurant.name}* is currently handled by Deli Dash.

We'll buy this order for you and your rider will contact you. Live restaurant status is not available for this partner yet."""
            )
        else:
            WhatsAppService.send_text(
                cls._restaurant_recipient(order),
                f"""Deli order request *{order.checkout_reference}*

Available?

Reply YES if you can prepare it now.
Reply NO if you cannot."""
            )

        if order.delivery_rider:
            WhatsAppService.send_text(
                order.delivery_rider.whatsapp_phone,
                f"""Deli delivery request *{order.checkout_reference}*

Available?

Reply YES if you can pick it up now.
Reply NO if you cannot."""
            )

        cls.notify_customer_order_ready(order)

        return order

    @classmethod
    def send_restaurant_order(
        cls,
        order,
    ):

        from whatsapp.services.whatsapp_service import WhatsAppService

        WhatsAppService.send_text(
            cls._restaurant_recipient(order),
            f"""✅ Order confirmed: *{order.checkout_reference}*

Items:
{cls.order_items_text(order)}

Please prepare only the items above.

Reply 1 after you give the rider this order to confirm dispatch of food."""
        )

    @classmethod
    def send_rider_order(
        cls,
        order,
    ):

        if not order.delivery_rider:
            return

        from whatsapp.services.whatsapp_service import WhatsAppService

        WhatsAppService.send_text(
            order.delivery_rider.whatsapp_phone,
            f"""✅ Delivery confirmed: *{order.checkout_reference}*

Restaurant:
{order.restaurant.name}
{order.restaurant.address}

Items:
{cls.order_items_text(order)}

Delivery address:
{order.delivery_address}

Customer phone:
{order.delivery_contact_phone or order.customer.phone}

Notes:
{order.delivery_notes or "None"}

Reply 1 after you deliver the order to the customer."""
        )

    @classmethod
    def send_deli_dash_delivery_order(
        cls,
        order,
    ):

        ops_number = getattr(
            settings,
            "DELI_DASH_WHATSAPP_NUMBER",
            "",
        )

        if not ops_number:
            return

        from whatsapp.services.whatsapp_service import WhatsAppService

        WhatsAppService.send_text(
            ops_number,
            f"""🚚 Deli Dash delivery job *{order.checkout_reference}*

Restaurant:
{order.restaurant.name}
{order.restaurant.address}

Items:
{cls.order_items_text(order)}

Delivery address:
{order.delivery_address}

Customer:
{order.customer.name or order.customer.phone}

Customer phone:
{order.delivery_contact_phone or order.customer.phone}

Notes:
{order.delivery_notes or "None"}"""
        )

    @classmethod
    def notify_customer_order_ready(
        cls,
        order,
    ):

        if (
            order.restaurant_availability_status == Order.PROVIDER_ACCEPTED
            and order.rider_availability_status == Order.PROVIDER_ACCEPTED
        ):
            order.status = Order.STATUS_ACCEPTED
            order.save(
                update_fields=[
                    "status",
                    "updated_at",
                ]
            )

            from whatsapp.services.whatsapp_service import WhatsAppService

            if not order.delivery_rider:
                cls.send_deli_dash_delivery_order(order)

            partner_note = (
                "\n\nDeli Dash will buy this from the restaurant for you. Live restaurant status is not available for this partner yet."
                if order.restaurant.send_orders_to_deli_dash
                else ""
            )

            WhatsAppService.send_list(
                order.customer.phone,
                f"""✅ Your order *{order.checkout_reference}* is confirmed.

{order.restaurant.name} is preparing your food.

Delivery:
{order.delivery_rider.name if order.delivery_rider else DeliveryService.DELI_DASH_NAME}

We'll keep you posted.{partner_note}

{cls.order_tracking_text(order)}""",
                cls.post_payment_action_rows(),
                "Order actions",
                "Reply 1, 2, 3, 4, 5, or 6.",
            )

    @classmethod
    def handle_provider_reply(
        cls,
        phone,
        message,
    ):

        command = message.lower().strip()

        if command in (
            "1",
            "dispatched",
            "picked up",
            "pickup",
            "delivered",
            "done",
            "complete",
            "completed",
        ) and cls._handle_provider_progress(phone, command):
            return True

        affirmative = command in (
            "1",
            "yes",
            "y",
            "available",
            "avail",
            "ok",
            "okay",
            "ready",
        )
        negative = command in (
            "no",
            "n",
            "not available",
            "busy",
            "decline",
        )

        if not affirmative and not negative:
            return False

        order = cls._pending_provider_order_for_phone(phone)

        if not order:
            return False

        status = (
            Order.PROVIDER_ACCEPTED
            if affirmative
            else Order.PROVIDER_DECLINED
        )

        from whatsapp.services.whatsapp_service import WhatsAppService

        if cls._phone_matches_restaurant(order, phone):
            order.restaurant_availability_status = status
            order.save(
                update_fields=[
                    "restaurant_availability_status",
                    "updated_at",
                ]
            )

            if affirmative:
                cls.send_restaurant_order(order)
            else:
                WhatsAppService.send_text(
                    order.customer.phone,
                    f"😔 {order.restaurant.name} cannot prepare order *{order.checkout_reference}* right now. We'll contact you to resolve it."
                )

            cls.notify_customer_order_ready(order)
            return True

        if order.delivery_rider and cls._phone_matches_rider(order, phone):
            order.rider_availability_status = status
            order.save(
                update_fields=[
                    "rider_availability_status",
                    "updated_at",
                ]
            )

            if affirmative:
                cls.send_rider_order(order)
                cls.notify_customer_order_ready(order)
            else:
                cls.offer_delisend_fallback(order)

            return True

        return False

    @classmethod
    def _handle_provider_progress(
        cls,
        phone,
        command,
    ):

        order = cls._active_provider_order_for_phone(phone)

        if not order:
            return False

        from whatsapp.services.whatsapp_service import WhatsAppService

        if cls._phone_matches_restaurant(order, phone):
            if (
                command in (
                    "delivered",
                    "done",
                    "complete",
                    "completed",
                )
                and not order.delivery_rider
            ):
                cls.mark_delivered(order)
                return True

            if order.status in (
                Order.STATUS_ACCEPTED,
                Order.STATUS_PREPARING,
            ):
                order.status = Order.STATUS_ON_THE_WAY
                order.save(
                    update_fields=[
                        "status",
                        "updated_at",
                    ]
                )

                WhatsAppService.send_list(
                    order.customer.phone,
                    f"""🚚 Your order *{order.checkout_reference}* is on the way.

The food has been handed to the rider.

{cls.order_tracking_text(order)}""",
                    cls.post_payment_action_rows(),
                    "Order actions",
                    "Reply 1, 2, 3, 4, 5, or 6.",
                )

                WhatsAppService.send_text(
                    phone,
                    f"✅ Dispatch confirmed for *{order.checkout_reference}*."
                )

                return True

        if order.delivery_rider and cls._phone_matches_rider(order, phone):
            if order.status in (
                Order.STATUS_ACCEPTED,
                Order.STATUS_PREPARING,
                Order.STATUS_ON_THE_WAY,
            ):
                cls.mark_delivered(order)
                WhatsAppService.send_text(
                    phone,
                    f"✅ Delivery confirmed for *{order.checkout_reference}*."
                )
                return True

        return False

    @classmethod
    def _pending_provider_order_for_phone(
        cls,
        phone,
    ):

        orders = (
            Order.objects
            .filter(
                status=Order.STATUS_PAID,
            )
            .select_related(
                "restaurant",
                "delivery_rider",
                "customer",
            )
            .prefetch_related(
                "items",
            )
            .order_by(
                "-created_at",
            )[:20]
        )

        for order in orders:
            if (
                cls._phone_matches_restaurant(order, phone)
                and order.restaurant_availability_status == Order.PROVIDER_ASKED
            ):
                return order

            if (
                order.delivery_rider
                and cls._phone_matches_rider(order, phone)
                and order.rider_availability_status == Order.PROVIDER_ASKED
            ):
                return order

        return None

    @classmethod
    def _active_provider_order_for_phone(
        cls,
        phone,
    ):

        orders = (
            Order.objects
            .filter(
                status__in=[
                    Order.STATUS_ACCEPTED,
                    Order.STATUS_PREPARING,
                    Order.STATUS_ON_THE_WAY,
                ],
            )
            .select_related(
                "restaurant",
                "delivery_rider",
                "customer",
            )
            .prefetch_related(
                "items",
            )
            .order_by(
                "-created_at",
            )[:20]
        )

        for order in orders:
            if cls._phone_matches_restaurant(order, phone):
                return order

            if (
                order.delivery_rider
                and cls._phone_matches_rider(order, phone)
            ):
                return order

        return None

    @staticmethod
    def _restaurant_recipient(order):

        if order.restaurant.send_orders_to_deli_dash:
            return (
                getattr(settings, "DELI_DASH_WHATSAPP_NUMBER", "")
                or order.restaurant.whatsapp_number
                or order.restaurant.phone
            )

        return order.restaurant.whatsapp_number or order.restaurant.phone

    @staticmethod
    def _phone_matches_restaurant(order, phone):

        if (
            order.restaurant.send_orders_to_deli_dash
            and getattr(settings, "DELI_DASH_WHATSAPP_NUMBER", "")
            and phone == settings.DELI_DASH_WHATSAPP_NUMBER
        ):
            return True

        return phone in {
            order.restaurant.phone,
            order.restaurant.whatsapp_number,
        }

    @staticmethod
    def _phone_matches_rider(order, phone):

        return order.delivery_rider and phone in {
            order.delivery_rider.phone,
            order.delivery_rider.whatsapp_number,
        }

    @classmethod
    def check_provider_timeouts(cls):

        cutoff = timezone.now() - timedelta(
            minutes=cls.PROVIDER_TIMEOUT_MINUTES,
        )

        orders = (
            Order.objects
            .filter(
                status=Order.STATUS_PAID,
                fallback_status=Order.FALLBACK_NOT_NEEDED,
            )
            .select_related(
                "customer",
                "restaurant",
                "delivery_rider",
            )
        )

        for order in orders:
            restaurant_timed_out = (
                order.restaurant_availability_status == Order.PROVIDER_ASKED
                and order.restaurant_asked_at
                and order.restaurant_asked_at <= cutoff
            )
            rider_timed_out = (
                order.rider_availability_status == Order.PROVIDER_ASKED
                and order.rider_asked_at
                and order.rider_asked_at <= cutoff
            )

            if not restaurant_timed_out and not rider_timed_out:
                continue

            if restaurant_timed_out:
                order.restaurant_availability_status = Order.PROVIDER_TIMEOUT

            if rider_timed_out:
                order.rider_availability_status = Order.PROVIDER_TIMEOUT

            order.save(
                update_fields=[
                    "restaurant_availability_status",
                    "rider_availability_status",
                    "updated_at",
                ]
            )

            if rider_timed_out:
                cls.offer_delisend_fallback(order)
                continue

            if restaurant_timed_out:
                from whatsapp.services.whatsapp_service import WhatsAppService

                WhatsAppService.send_text(
                    order.customer.phone,
                    f"""We could not confirm *{order.restaurant.name}* for order *{order.checkout_reference}* in time.

Deli Dash will contact you to resolve this order or arrange a replacement."""
                )

    @classmethod
    def offer_delisend_fallback(cls, order):

        order.fallback_status = Order.FALLBACK_OFFERED
        order.fallback_delivery_fee = DeliveryService.DELI_DASH_FEE
        order.save(
            update_fields=[
                "fallback_status",
                "fallback_delivery_fee",
                "updated_at",
            ]
        )

        from users.constants import DELISEND_CONFIRMATION
        from users.models import ConversationState
        from whatsapp.services.state_service import StateService
        from whatsapp.services.whatsapp_service import WhatsAppService

        conversation, _ = ConversationState.objects.get_or_create(
            customer=order.customer,
        )
        StateService.set_order(conversation, order)
        StateService.set(conversation, DELISEND_CONFIRMATION)

        delta = DeliveryService.delisend_delta(
            order.delivery_fee,
        )

        WhatsAppService.send_text(
            order.customer.phone,
            f"""We could not confirm the selected rider for order *{order.checkout_reference}*.

We can deliver it with Deli Dash for {delta}.

Reply YES to continue with Deli Dash.
Reply NO to cancel."""
        )

    @classmethod
    def accept_delisend_fallback(cls, order):

        order.delivery_rider = None
        order.delivery_fee = order.fallback_delivery_fee
        order.total = (
            order.subtotal
            + order.delivery_fee
            + order.customer_service_fee
            + order.maintenance_fee
        )
        order.rider_availability_status = Order.PROVIDER_ACCEPTED
        order.fallback_status = Order.FALLBACK_ACCEPTED
        order.status = Order.STATUS_ACCEPTED
        order.save(
            update_fields=[
                "delivery_rider",
                "delivery_fee",
                "total",
                "rider_availability_status",
                "fallback_status",
                "status",
                "updated_at",
            ]
        )

        from whatsapp.services.whatsapp_service import WhatsAppService

        if order.restaurant_availability_status == Order.PROVIDER_ACCEPTED:
            cls.notify_customer_order_ready(order)
        else:
            WhatsAppService.send_text(
                order.customer.phone,
                f"✅ Deli Dash accepted for order *{order.checkout_reference}*. We are confirming the restaurant now."
            )

        return order

    @classmethod
    def decline_delisend_fallback(cls, order):

        order.fallback_status = Order.FALLBACK_DECLINED
        order.status = Order.STATUS_CANCELLED
        order.save(
            update_fields=[
                "fallback_status",
                "status",
                "updated_at",
            ]
        )

        from whatsapp.services.whatsapp_service import WhatsAppService

        WhatsAppService.send_text(
            order.customer.phone,
            f"Order *{order.checkout_reference}* has been cancelled."
        )

        return order
