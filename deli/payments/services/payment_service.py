import base64
import hashlib
import hmac
import logging
from decimal import Decimal
from datetime import timedelta
from urllib.parse import (
    parse_qsl,
    urlencode,
    urlparse,
    urlunparse,
)
from uuid import uuid4

import requests

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from orders.services.order_service import OrderService
from payments.models import Payment

logger = logging.getLogger(__name__)


class PaymentService:

    TOKEN_CACHE_KEY = "nomba_access_token"
    TOKEN_EXPIRY_KEY = "nomba_access_token_expiry"

    @staticmethod
    def api_root():

        base = getattr(
            settings,
            "NOMBA_BASE_URL",
            "https://sandbox.nomba.com/v1",
        ).rstrip("/")

        if base.endswith("/v1") or base.endswith("/v2"):
            return base.rsplit("/", 1)[0]

        return base

    @classmethod
    def base_url(cls):

        return f"{cls.api_root()}/v1"

    @classmethod
    def v2_base_url(cls):

        return f"{cls.api_root()}/v2"

    @classmethod
    def is_sandbox(cls):

        return "sandbox.nomba.com" in cls.api_root()

    @classmethod
    def checkout_base_url(cls):

        return cls.base_url()

    @staticmethod
    def _amount_decimal(amount):

        return Decimal(str(amount)).quantize(Decimal("0.01"))

    @classmethod
    def checkout_amount(cls, amount):

        return format(
            cls._amount_decimal(amount),
            ".2f",
        )

    @classmethod
    def transfer_amount(cls, amount):

        amount_decimal = cls._amount_decimal(amount)

        if amount_decimal == amount_decimal.to_integral_value():
            return int(amount_decimal)

        return float(amount_decimal)

    @staticmethod
    def _require_setting(name):

        value = getattr(settings, name, None)

        if not value:
            raise RuntimeError(f"{name} is not configured")

        return value

    @classmethod
    def get_access_token(cls):

        token = cache.get(cls.TOKEN_CACHE_KEY)
        expiry = cache.get(cls.TOKEN_EXPIRY_KEY)

        if token and expiry and expiry > timezone.now():
            return token

        account_id = cls._require_setting("NOMBA_ACCOUNT_ID")

        response = requests.post(
            f"{cls.base_url()}/auth/token/issue",
            headers={
                "Content-Type": "application/json",
                "accountId": account_id,
            },
            json={
                "grant_type": "client_credentials",
                "client_id": cls._require_setting("NOMBA_CLIENT_ID"),
                "client_secret": cls._require_setting("NOMBA_CLIENT_SECRET"),
            },
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()["data"]
        token = data["access_token"]
        expiry = timezone.now() + timedelta(minutes=55)

        cache.set(cls.TOKEN_CACHE_KEY, token, timeout=55 * 60)
        cache.set(cls.TOKEN_EXPIRY_KEY, expiry, timeout=55 * 60)

        return token

    @classmethod
    def _headers(cls):

        return {
            "Authorization": f"Bearer {cls.get_access_token()}",
            "accountId": cls._require_setting("NOMBA_ACCOUNT_ID"),
            "Content-Type": "application/json",
        }

    @classmethod
    def callback_url(cls):

        callback_url = (
            getattr(settings, "NOMBA_CALLBACK_URL", "")
            or (
                f"{settings.PUBLIC_BASE_URL}/api/v1/payments/return/"
                if getattr(settings, "PUBLIC_BASE_URL", "")
                else ""
            )
        ).strip()

        parsed = urlparse(callback_url)

        if parsed.scheme != "https" or not parsed.netloc:
            raise RuntimeError(
                "NOMBA_CALLBACK_URL must be a clean public HTTPS URL, for example "
                "https://your-domain/api/v1/payments/return/. Without this, Nomba may redirect to its homepage."
            )

        return callback_url

    @staticmethod
    def callback_url_with_reference(
        callback_url,
        reference,
    ):

        parsed = urlparse(callback_url)
        query = dict(parse_qsl(parsed.query))
        query["reference"] = reference

        return urlunparse(
            parsed._replace(
                query=urlencode(query),
            )
        )

    @classmethod
    def create_checkout(cls, order):

        merchant_ref = f"PAY-{uuid4().hex.upper()}"

        callback_url = cls.callback_url_with_reference(
            cls.callback_url(),
            merchant_ref,
        )

        order_payload = {
            "orderReference": merchant_ref,
            "amount": cls.checkout_amount(order.total),
            "currency": "NGN",
            "customerEmail": f"{order.customer.phone}@deli.local",
            "customerId": f"cus_{order.customer.id}",
            "callbackUrl": callback_url,
        }

        sub_account_id = getattr(settings, "NOMBA_SUB_ACCOUNT_ID", "")

        if sub_account_id:
            order_payload["accountId"] = sub_account_id

        allowed_methods = getattr(
            settings,
            "NOMBA_ALLOWED_PAYMENT_METHODS",
            [],
        )

        if allowed_methods:
            order_payload["allowedPaymentMethods"] = allowed_methods

        payload = {
            "order": order_payload,
        }

        logger.info(
            "Creating Nomba checkout",
            extra={
                "merchantTxRef": merchant_ref,
                "order": order.checkout_reference,
                "amount": order_payload["amount"],
                "callbackUrl": callback_url,
            },
        )

        response = requests.post(
            f"{cls.checkout_base_url()}/checkout/order",
            headers=cls._headers(),
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        raw = response.json()
        data = raw.get("data", {})
        nomba_reference = (
            data.get("orderReference")
            or data.get("order_reference")
            or merchant_ref
        )
        checkout_url = (
            data.get("checkoutUrl")
            or data.get("checkoutLink")
            or data.get("paymentLink")
            or ""
        )

        if not checkout_url:
            raise RuntimeError(
                "Nomba did not return a checkout URL."
            )

        payment = Payment.objects.create(
            order=order,
            merchant_reference=merchant_ref,
            checkout_reference=nomba_reference,
            checkout_url=checkout_url,
            amount=order.total,
            raw_response=raw,
        )

        OrderService.mark_payment_pending(
            order,
            checkout_url=checkout_url,
            payment_reference=merchant_ref,
        )

        return payment

    @classmethod
    def get(cls, endpoint, params=None):

        response = requests.get(
            f"{cls.base_url()}{endpoint}",
            headers=cls._headers(),
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def post(cls, endpoint, payload):

        response = requests.post(
            f"{cls.base_url()}{endpoint}",
            headers=cls._headers(),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def lookup_bank_account(
        cls,
        bank_code,
        account_number,
    ):

        response = requests.post(
            f"{cls.base_url()}/transfers/bank/lookup",
            headers=cls._headers(),
            json={
                "bankCode": bank_code,
                "accountNumber": account_number,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def transfer_to_bank(
        cls,
        amount,
        bank_code,
        account_number,
        sender_name,
        narration,
        merchant_reference,
        expected_account_name="",
    ):

        lookup = cls.lookup_bank_account(
            bank_code,
            account_number,
        )

        data = lookup.get("data", {})
        account_name = (
            data.get("accountName")
            or data.get("account_name")
            or data.get("name")
            or ""
        )

        if not account_name:
            raise RuntimeError("Nomba could not resolve recipient account name.")

        if expected_account_name and not cls._account_name_matches(
            expected_account_name,
            account_name,
        ):
            raise RuntimeError(
                f"Resolved account name '{account_name}' does not match expected '{expected_account_name}'."
            )

        sub_account_id = cls._require_setting("NOMBA_SUB_ACCOUNT_ID")
        transfer_amount = cls.transfer_amount(amount)

        payload = {
            "amount": transfer_amount,
            "bankCode": bank_code,
            "accountNumber": account_number,
            "accountName": account_name,
            "senderName": sender_name,
            "narration": narration,
            "merchantTxRef": merchant_reference,
        }

        logger.info(
            "Initiating Nomba transfer",
            extra={
                "merchantTxRef": merchant_reference,
                "amount": transfer_amount,
                "bankCode": bank_code,
            },
        )

        response = requests.post(
            f"{cls.v2_base_url()}/transfers/bank/{sub_account_id}",
            headers=cls._headers(),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()

        return {
            "lookup": lookup,
            "transfer": response.json(),
            "resolved_account_name": account_name,
        }

    @staticmethod
    def _account_name_matches(expected, resolved):

        expected_parts = {
            part
            for part in expected.lower().replace(".", " ").split()
            if len(part) > 1
        }
        resolved_text = resolved.lower()

        if not expected_parts:
            return True

        return any(part in resolved_text for part in expected_parts)

    @classmethod
    def verify_webhook(cls, body, headers, payload=None):

        signature = headers.get("nomba-signature") or headers.get(
            "Nomba-Signature",
            "",
        )

        secret = getattr(settings, "NOMBA_WEBHOOK_SECRET", "") or ""

        if not signature or not secret:
            return False

        expected_hex = hmac.new(
            secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()

        if hmac.compare_digest(expected_hex, signature):
            return True

        if not payload:
            return False

        timestamp = headers.get("nomba-timestamp") or headers.get(
            "Nomba-Timestamp",
            "",
        )

        try:
            merchant = payload["data"]["merchant"]
            transaction = payload["data"]["transaction"]
            signed = ":".join(
                [
                    payload.get("event_type") or payload.get("event") or "",
                    payload.get("requestId") or payload.get("request_id") or "",
                    merchant.get("userId", ""),
                    merchant.get("walletId", ""),
                    transaction.get("transactionId", ""),
                    transaction.get("type", ""),
                    transaction.get("time", ""),
                    transaction.get("responseCode", ""),
                    timestamp,
                ]
            )
            expected_base64 = base64.b64encode(
                hmac.new(
                    secret.encode(),
                    signed.encode(),
                    hashlib.sha256,
                ).digest()
            ).decode()
        except (KeyError, TypeError):
            return False

        return hmac.compare_digest(expected_base64, signature)

    @staticmethod
    def event_type(payload):

        return (
            payload.get("event")
            or payload.get("event_type")
            or payload.get("type")
            or ""
        )

    @staticmethod
    def request_id(payload):

        return (
            payload.get("requestId")
            or payload.get("request_id")
            or payload.get("id")
            or str(uuid4())
        )

    @staticmethod
    def merchant_reference(payload):

        data = payload.get("data", {})

        candidates = [
            payload.get("merchantTxRef"),
            payload.get("merchant_reference"),
            payload.get("orderReference"),
            payload.get("order_reference"),
            payload.get("reference"),
            data.get("merchantTxRef"),
            data.get("merchant_reference"),
            data.get("orderReference"),
            data.get("order_reference"),
            data.get("reference"),
            data.get("transaction", {}).get("merchantTxRef"),
            data.get("transaction", {}).get("orderReference"),
            data.get("transaction", {}).get("reference"),
        ]

        for candidate in candidates:
            if candidate:
                return candidate

        return ""

    @classmethod
    def payment_for_reference(
        cls,
        reference,
        lock=False,
    ):

        queryset = Payment.objects.select_related(
            "order",
        )

        if lock:
            queryset = queryset.select_for_update()

        return (
            queryset
            .filter(
                Q(merchant_reference=reference)
                | Q(checkout_reference=reference)
                | Q(order__payment_reference=reference)
                | Q(order__checkout_reference=reference)
                | Q(raw_response__data__orderReference=reference)
                | Q(raw_response__data__order_reference=reference)
            )
            .first()
        )

    @classmethod
    def handle_event(cls, payload):

        event = cls.event_type(payload).lower()
        merchant_reference = cls.merchant_reference(payload)

        if not merchant_reference:
            return None

        if event in (
            "payment_success",
            "checkout.payment.success",
            "checkout_success",
            "successful",
        ) or "success" in event:
            return cls.handle_payment_success(
                merchant_reference,
                payload,
            )

        if event in (
            "payment_failed",
            "checkout.payment.failed",
            "checkout_failed",
            "failed",
        ) or "failed" in event:
            return cls.handle_payment_failed(
                merchant_reference,
                payload,
            )

        return None

    @classmethod
    def handle_payment_success(
        cls,
        merchant_reference,
        payload,
    ):

        with transaction.atomic():
            payment = cls.payment_for_reference(
                merchant_reference,
                lock=True,
            )

            if not payment:
                raise Payment.DoesNotExist(
                    f"No local payment exists for {merchant_reference}."
                )

            if payment.status != Payment.STATUS_SUCCESS:
                payment.status = Payment.STATUS_SUCCESS
                payment.raw_response = payload
                payment.paid_at = timezone.now()
                payment.save(
                    update_fields=[
                        "status",
                        "raw_response",
                        "paid_at",
                        "updated_at",
                    ]
                )

        payment.order.refresh_from_db()

        if payment.order.status in (
            payment.order.STATUS_PENDING,
            payment.order.STATUS_AWAITING_PAYMENT,
        ):
            OrderService.mark_paid(payment.order)
            payment.order.refresh_from_db()
            OrderService.notify_customer_payment_confirmed(payment.order)
            OrderService.ask_providers_availability(payment.order)
        elif (
            payment.order.status == payment.order.STATUS_PAID
            and payment.order.restaurant_availability_status
            == payment.order.PROVIDER_PENDING
            and payment.order.rider_availability_status
            == payment.order.PROVIDER_PENDING
        ):
            OrderService.notify_customer_payment_confirmed(payment.order)
            OrderService.ask_providers_availability(payment.order)

        return payment

    @classmethod
    def handle_payment_failed(
        cls,
        merchant_reference,
        payload,
    ):

        payment = cls.payment_for_reference(
            merchant_reference,
        )

        if not payment:
            raise Payment.DoesNotExist(
                f"No local payment exists for {merchant_reference}."
            )

        payment.status = Payment.STATUS_FAILED
        payment.raw_response = payload
        payment.save(
            update_fields=[
                "status",
                "raw_response",
                "updated_at",
            ]
        )

        OrderService.mark_cancelled(payment.order)

        return payment

    @classmethod
    def requery_checkout(cls, merchant_reference):

        try:
            response = requests.get(
                f"{cls.checkout_base_url()}/checkout/order/{merchant_reference}",
                headers=cls._headers(),
                timeout=30,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as exc:
            if (
                not cls.is_sandbox()
                or exc.response is None
                or exc.response.status_code != 404
            ):
                raise

        response = requests.get(
            f"{cls.api_root()}/sandbox/checkout/transaction",
            headers=cls._headers(),
            params={
                "idType": "orderReference",
                "id": merchant_reference,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def confirm_checkout(cls, merchant_reference):

        payment = cls.payment_for_reference(
            merchant_reference,
        )

        if not payment:
            raise Payment.DoesNotExist(
                f"No local payment exists for {merchant_reference}."
            )

        references = []

        for reference in (
            merchant_reference,
            payment.merchant_reference,
            payment.checkout_reference,
            payment.order.payment_reference,
            payment.order.checkout_reference,
        ):
            if reference and reference not in references:
                references.append(reference)

        raw = None
        last_error = None

        for reference in references:
            try:
                raw = cls.requery_checkout(reference)
            except requests.RequestException as exc:
                last_error = exc
                continue

            if cls._response_is_success(raw):
                return cls.handle_payment_success(
                    reference,
                    raw,
                )

            if cls._response_is_failed(raw):
                return cls.handle_payment_failed(
                    reference,
                    raw,
                )

        if raw is None and last_error:
            raise last_error

        payment.raw_response = raw
        payment.save(
            update_fields=[
                "raw_response",
                "updated_at",
            ]
        )

        return payment

    @classmethod
    def _response_is_success(cls, payload):

        return any(
            token in {
                "success",
                "successful",
                "paid",
                "completed",
                "approved",
                "payment successful",
            }
            or "payment successful" in token
            or (key == "responsecode" and token == "00")
            or token.endswith("_success")
            or token.endswith(".success")
            for key, token in cls._status_tokens(payload)
        )

    @classmethod
    def _response_is_failed(cls, payload):

        return any(
            token in {
                "failed",
                "failure",
                "declined",
                "cancelled",
                "canceled",
                "reversed",
                "abandoned",
            }
            or token.endswith("_failed")
            or token.endswith(".failed")
            for _, token in cls._status_tokens(payload)
        )

    @classmethod
    def _status_tokens(cls, payload):

        status_keys = {
            "status",
            "responsecode",
            "responsestatus",
            "paymentstatus",
            "orderstatus",
            "statuscode",
            "transactionstatus",
        }

        tokens = []

        def collect(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    normalized_key = str(key).replace("_", "").lower()
                    if normalized_key in status_keys:
                        tokens.append(
                            (
                                normalized_key,
                                str(child).strip().lower(),
                            )
                        )
                    collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)

        root = (
            payload.get("data", payload)
            if isinstance(payload, dict)
            else payload
        )
        collect(root)

        return tokens
