from decimal import Decimal

from django.core.management.base import BaseCommand

from orders.models import Order
from payments.models import Payout
from payments.services.payment_service import PaymentService


class Command(BaseCommand):
    help = "Create or execute Nomba payouts for delivered orders."

    def add_arguments(self, parser):

        parser.add_argument("--order", dest="order_reference")
        parser.add_argument(
            "--recipient",
            choices=["all", "restaurant", "rider"],
            default="all",
        )
        parser.add_argument(
            "--execute",
            action="store_true",
            help="Actually call Nomba transfer APIs. Without this flag the command only prepares local payout rows.",
        )

    def handle(self, *args, **options):

        orders = Order.objects.filter(
            status=Order.STATUS_DELIVERED,
        ).select_related(
            "restaurant",
            "delivery_rider",
        )

        if options.get("order_reference"):
            orders = orders.filter(
                checkout_reference=options["order_reference"],
            )

        count = 0

        for order in orders:
            count += self._handle_order(
                order,
                options["recipient"],
                options["execute"],
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Payout command completed. {count} payout row(s) handled."
            )
        )

    def _handle_order(
        self,
        order,
        recipient,
        execute,
    ):

        handled = 0

        if recipient in ("all", "restaurant"):
            handled += self._handle_restaurant_payout(
                order,
                execute,
            )

        if recipient in ("all", "rider") and order.delivery_rider:
            handled += self._handle_rider_payout(
                order,
                execute,
            )

        return handled

    def _handle_restaurant_payout(
        self,
        order,
        execute,
    ):

        restaurant = order.restaurant

        if not restaurant.bank_code or not restaurant.account_number:
            self.stdout.write(
                self.style.WARNING(
                    f"{order.checkout_reference}: restaurant bank details missing."
                )
            )
            return 0

        payout, _ = Payout.objects.get_or_create(
            order=order,
            recipient_type=Payout.RECIPIENT_RESTAURANT,
            defaults={
                "amount": max(
                    order.subtotal - order.restaurant_platform_fee,
                    Decimal("0.00"),
                ),
                "bank_code": restaurant.bank_code,
                "account_number": restaurant.account_number,
                "expected_account_name": restaurant.account_name,
                "merchant_reference": f"POUT-{order.checkout_reference}-REST",
            },
        )

        return self._execute_payout(
            payout,
            sender_name="Deli",
            narration=f"Deli restaurant payout {order.checkout_reference}",
            execute=execute,
        )

    def _handle_rider_payout(
        self,
        order,
        execute,
    ):

        rider = order.delivery_rider

        if not rider.bank_code or not rider.account_number:
            self.stdout.write(
                self.style.WARNING(
                    f"{order.checkout_reference}: rider bank details missing."
                )
            )
            return 0

        payout, _ = Payout.objects.get_or_create(
            order=order,
            recipient_type=Payout.RECIPIENT_RIDER,
            defaults={
                "amount": max(
                    order.delivery_fee - order.rider_platform_fee,
                    Decimal("0.00"),
                ),
                "bank_code": rider.bank_code,
                "account_number": rider.account_number,
                "expected_account_name": rider.account_name,
                "merchant_reference": f"POUT-{order.checkout_reference}-RIDER",
            },
        )

        return self._execute_payout(
            payout,
            sender_name="Deli",
            narration=f"Deli rider payout {order.checkout_reference}",
            execute=execute,
        )

    def _execute_payout(
        self,
        payout,
        sender_name,
        narration,
        execute,
    ):

        if payout.status == Payout.STATUS_SUCCESS:
            self.stdout.write(
                f"{payout.merchant_reference}: already successful."
            )
            return 1

        if not execute:
            self.stdout.write(
                f"{payout.merchant_reference}: prepared, not executed. Add --execute to transfer."
            )
            return 1

        payout.status = Payout.STATUS_PROCESSING
        payout.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        try:
            response = PaymentService.transfer_to_bank(
                amount=payout.amount,
                bank_code=payout.bank_code,
                account_number=payout.account_number,
                sender_name=sender_name,
                narration=narration,
                merchant_reference=payout.merchant_reference,
                expected_account_name=payout.expected_account_name,
            )
        except Exception as exc:
            payout.status = Payout.STATUS_FAILED
            payout.raw_response = {
                "error": str(exc),
            }
            payout.save(
                update_fields=[
                    "status",
                    "raw_response",
                    "updated_at",
                ]
            )
            self.stdout.write(
                self.style.ERROR(
                    f"{payout.merchant_reference}: failed - {exc}"
                )
            )
            return 1

        payout.status = Payout.STATUS_SUCCESS
        payout.resolved_account_name = response["resolved_account_name"]
        payout.raw_response = response
        payout.save(
            update_fields=[
                "status",
                "resolved_account_name",
                "raw_response",
                "updated_at",
            ]
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"{payout.merchant_reference}: transfer sent."
            )
        )
        return 1
