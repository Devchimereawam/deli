from django.core.management.base import BaseCommand, CommandError

from payments.models import Payment
from payments.services.payment_service import PaymentService


class Command(BaseCommand):
    help = "Requery a Nomba checkout order and process success/failure if returned."

    def add_arguments(self, parser):

        parser.add_argument("reference")

    def handle(self, *args, **options):

        reference = options["reference"]

        payment = Payment.objects.filter(
            merchant_reference=reference,
        ).first()

        if not payment:
            payment = Payment.objects.filter(
                order__checkout_reference=reference,
            ).first()

        if not payment:
            raise CommandError(
                f"No local payment found for {reference}."
            )

        response = PaymentService.requery_checkout(
            payment.merchant_reference,
        )

        status_text = str(response).lower()

        if "success" in status_text or "paid" in status_text:
            PaymentService.handle_payment_success(
                payment.merchant_reference,
                response,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Nomba reports success for {payment.merchant_reference}."
                )
            )
            return

        if "failed" in status_text or "cancel" in status_text:
            PaymentService.handle_payment_failed(
                payment.merchant_reference,
                response,
            )
            self.stdout.write(
                self.style.ERROR(
                    f"Nomba reports failure for {payment.merchant_reference}."
                )
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"Nomba checkout is not successful yet for {payment.merchant_reference}."
            )
        )
        self.stdout.write(str(response))
