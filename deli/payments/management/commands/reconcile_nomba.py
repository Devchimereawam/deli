from django.conf import settings
from django.core.management.base import BaseCommand
from decimal import Decimal

from payments.models import Payment
from payments.services.payment_service import PaymentService


class Command(BaseCommand):
    help = "Compare successful Nomba transactions against local payments."

    def add_arguments(self, parser):

        parser.add_argument("--date-from", dest="date_from")
        parser.add_argument("--date-to", dest="date_to")

    def handle(self, *args, **options):

        params = {
            "status": "success",
        }

        if options.get("date_from"):
            params["dateFrom"] = options["date_from"]

        if options.get("date_to"):
            params["dateTo"] = options["date_to"]

        sub_account_id = getattr(
            settings,
            "NOMBA_SUB_ACCOUNT_ID",
            "",
        )

        if sub_account_id:
            endpoint = f"/transactions/accounts/{sub_account_id}"
        else:
            endpoint = "/transactions"

        response = PaymentService.get(
            endpoint,
            params=params,
        )

        data = response.get("data", {})
        transactions = (
            data.get("transactions")
            or data.get("content")
            or data.get("items")
            or []
        )

        drift_count = 0

        for transaction in transactions:
            reference = (
                transaction.get("merchantTxRef")
                or transaction.get("orderReference")
                or transaction.get("reference")
            )

            if not reference:
                continue

            payment = Payment.objects.filter(
                merchant_reference=reference,
            ).first()

            if not payment:
                drift_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Orphan Nomba transaction: {reference}"
                    )
                )
                continue

            nomba_amount = transaction.get("amount")

            if nomba_amount is not None and not self._amount_matches(
                payment.amount,
                nomba_amount,
            ):
                drift_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Amount drift for {reference}: local={payment.amount} nomba={nomba_amount}"
                    )
                )

        if drift_count:
            self.stdout.write(
                self.style.WARNING(
                    f"Reconciliation completed with {drift_count} issue(s)."
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                "Reconciliation completed with no drift."
            )
        )

    @staticmethod
    def _amount_matches(local_amount, nomba_amount):

        local = Decimal(str(local_amount)).quantize(Decimal("0.01"))
        remote = Decimal(str(nomba_amount)).quantize(Decimal("0.01"))

        if remote == local:
            return True

        return remote == (local * Decimal("100")).quantize(Decimal("0.01"))
