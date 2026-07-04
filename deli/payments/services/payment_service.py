import hashlib
import hmac
import os
from datetime import timedelta
from uuid import uuid4

import requests

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from orders.services.order_service import OrderService
from payments.models import Payment


class PaymentService:

    TOKEN_CACHE_KEY = "nomba_access_token"

    TOKEN_EXPIRY_KEY = "nomba_access_token_expiry"

    @staticmethod
    def base_url():

        return getattr(
            settings,
            "NOMBA_BASE_URL",
            "https://sandbox.api.nomba.com/v1",
        )

    @classmethod
    def get_access_token(cls):

        token = cache.get(
            cls.TOKEN_CACHE_KEY,
        )

        expiry = cache.get(
            cls.TOKEN_EXPIRY_KEY,
        )

        if (
            token
            and expiry
            and expiry > timezone.now()
        ):

            return token

        response = requests.post(

            f"{cls.base_url()}/auth/token/issue",

            headers={

                "Content-Type": "application/json",

                "accountId": settings.NOMBA_ACCOUNT_ID,

            },

            json={

                "grant_type": "client_credentials",

                "client_id": settings.NOMBA_CLIENT_ID,

                "client_secret": settings.NOMBA_CLIENT_SECRET,

            },

            timeout=30,

        )

        response.raise_for_status()

        data = response.json()["data"]

        token = data["access_token"]

        expiry = timezone.now() + timedelta(
            minutes=55,
        )

        cache.set(
            cls.TOKEN_CACHE_KEY,
            token,
            timeout=55 * 60,
        )

        cache.set(
            cls.TOKEN_EXPIRY_KEY,
            expiry,
            timeout=55 * 60,
        )

        return token

    @classmethod
    def create_checkout(
        cls,
        order,
    ):

        token = cls.get_access_token()

        merchant_ref = (
            f"PAY-{uuid4().hex.upper()}"
        )

        response = requests.post(

            f"{cls.base_url()}/checkout/order",

            headers={

                "Authorization": f"Bearer {token}",

                "accountId": settings.NOMBA_ACCOUNT_ID,

                "Content-Type": "application/json",

            },

            json={

                "order": {

                    "orderReference": merchant_ref,

                    "amount": int(
                        order.total * 100
                    ),

                    "currency": "NGN",

                    "customerEmail": (
                        order.customer.email
                        or "customer@deli.app"
                    ),

                    "customerId": str(
                        order.customer.id
                    ),

                    "callbackUrl": (
                        settings.NOMBA_CALLBACK_URL
                    ),

                }

            },

            timeout=30,

        )

        response.raise_for_status()

        data = response.json()["data"]

        payment = Payment.objects.create(

            order=order,

            merchant_reference=merchant_ref,

            checkout_reference=merchant_ref,

            checkout_url=data["checkoutUrl"],

            amount=order.total,

            raw_response=response.json(),

        )

        OrderService.mark_payment_pending(

            order,

            checkout_url=data["checkoutUrl"],

            payment_reference=merchant_ref,

        )

        return payment

    @classmethod
    def verify_webhook(
        cls,
        body,
        signature,
    ):

        expected = hmac.new(

            settings.NOMBA_WEBHOOK_SECRET.encode(),

            body,

            hashlib.sha256,

        ).hexdigest()

        return hmac.compare_digest(
            expected,
            signature,
        )

    @classmethod
    def handle_payment_success(
        cls,
        merchant_reference,
        payload,
    ):

        payment = Payment.objects.select_related(
            "order",
        ).get(
            merchant_reference=merchant_reference,
        )

        payment.status = Payment.STATUS_SUCCESS

        payment.raw_response = payload

        payment.paid_at = timezone.now()

        payment.save()

        OrderService.mark_paid(
            payment.order,
        )

        return payment

    @classmethod
    def handle_payment_failed(
        cls,
        merchant_reference,
        payload,
    ):

        payment = Payment.objects.select_related(
            "order",
        ).get(
            merchant_reference=merchant_reference,
        )

        payment.status = Payment.STATUS_FAILED

        payment.raw_response = payload

        payment.save()

        OrderService.mark_cancelled(
            payment.order,
        )

        return payment