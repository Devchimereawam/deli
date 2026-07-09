from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from orders.models import Order
from orders.services.order_service import OrderService
from whatsapp.services.whatsapp_service import WhatsAppService


class Command(BaseCommand):
    help = "Confirm live order test steps without needing separate restaurant/rider/customer WhatsApp numbers."

    def add_arguments(self, parser):

        parser.add_argument(
            "--order",
            required=True,
            dest="order_reference",
            help="Deli order reference, for example ORD-ABC123.",
        )
        parser.add_argument(
            "--restaurant-dispatch",
            action="store_true",
            help="Mark restaurant dispatch/food handoff to rider.",
        )
        parser.add_argument(
            "--provider-delivered",
            action="store_true",
            help="Mark rider/restaurant delivery confirmation.",
        )
        parser.add_argument(
            "--customer-delivered",
            action="store_true",
            help="Mark customer delivery confirmation.",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Run restaurant dispatch, provider delivered, then customer delivered.",
        )
        parser.add_argument(
            "--no-whatsapp",
            action="store_true",
            help="Update the order without sending WhatsApp test notifications.",
        )

    def handle(self, *args, **options):

        actions = [
            options["restaurant_dispatch"],
            options["provider_delivered"],
            options["customer_delivered"],
            options["all"],
        ]

        if not any(actions):
            raise CommandError(
                "Choose at least one action: --restaurant-dispatch, --provider-delivered, --customer-delivered, or --all."
            )

        try:
            order = (
                Order.objects
                .select_related(
                    "customer",
                    "restaurant",
                    "delivery_rider",
                )
                .prefetch_related(
                    "items",
                )
                .get(
                    checkout_reference=options["order_reference"],
                )
            )
        except Order.DoesNotExist as exc:
            raise CommandError(
                f"Order {options['order_reference']} was not found."
            ) from exc

        send_whatsapp = not options["no_whatsapp"]

        if options["all"] or options["restaurant_dispatch"]:
            self._restaurant_dispatch(
                order,
                send_whatsapp=send_whatsapp,
            )

        if options["all"] or options["provider_delivered"]:
            order.refresh_from_db()
            OrderService.confirm_provider_delivery(order)
            self.stdout.write(
                self.style.SUCCESS(
                    f"{order.checkout_reference}: provider delivery confirmed."
                )
            )

        if options["all"] or options["customer_delivered"]:
            order.refresh_from_db()
            OrderService.confirm_customer_delivery(order)
            self.stdout.write(
                self.style.SUCCESS(
                    f"{order.checkout_reference}: customer delivery confirmed."
                )
            )

        order.refresh_from_db()
        self.stdout.write(
            self.style.SUCCESS(
                f"Final status: {order.get_status_display()}"
            )
        )
        self.stdout.write(
            f"Restaurant dispatch: {self._yes_no(order.restaurant_dispatch_confirmed_at)}"
        )
        self.stdout.write(
            f"Provider delivered: {self._yes_no(order.provider_delivery_confirmed_at)}"
        )
        self.stdout.write(
            f"Customer delivered: {self._yes_no(order.customer_delivery_confirmed_at)}"
        )

    def _restaurant_dispatch(
        self,
        order,
        send_whatsapp,
    ):

        update_fields = []

        if not order.restaurant_dispatch_confirmed_at:
            order.restaurant_dispatch_confirmed_at = timezone.now()
            update_fields.append("restaurant_dispatch_confirmed_at")

        if order.status in (
            Order.STATUS_PAID,
            Order.STATUS_ACCEPTED,
            Order.STATUS_PREPARING,
        ):
            order.status = Order.STATUS_ON_THE_WAY
            update_fields.append("status")

        if update_fields:
            update_fields.append("updated_at")
            order.save(
                update_fields=update_fields,
            )

        if send_whatsapp:
            WhatsAppService.send_list(
                order.customer.phone,
                f"""🚚 Test update for order *{order.checkout_reference}*

The restaurant dispatch step has been confirmed.

{OrderService.order_tracking_text(order)}""",
                OrderService.post_payment_action_rows(),
                "Order actions",
                "Reply 2 to confirm delivered after you receive the food.",
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"{order.checkout_reference}: restaurant dispatch confirmed."
            )
        )

    @staticmethod
    def _yes_no(value):

        return "yes" if value else "no"
