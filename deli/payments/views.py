import json
import logging
from html import escape
from urllib.parse import quote

from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from payments.models import Payment
from payments.models import NombaWebhookEvent
from payments.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


def payment_return(request):

    reference = (
        request.GET.get("orderReference")
        or request.GET.get("reference")
        or request.GET.get("merchantTxRef")
        or request.GET.get("merchantReference")
        or request.GET.get("order_reference")
        or ""
    )

    if not reference:
        return _payment_return_page(
            title="Return to WhatsApp",
            message="We received the payment return, but Nomba did not include an order reference. Return to WhatsApp and type track.",
        )

    try:
        payment = PaymentService.confirm_checkout(reference)
    except Payment.DoesNotExist:
        logger.warning(
            "Nomba return used unknown payment reference: %s",
            reference,
        )
        return _payment_return_page(
            title="Payment Received",
            message=(
                f"Nomba returned reference {escape(reference)}, but Deli could not match it locally yet. "
                "Return to WhatsApp and type track."
            ),
        )
    except Exception as exc:
        logger.exception("Nomba checkout requery failed: %s", exc)
        return _payment_return_page(
            title="Payment Processing",
            message=(
                "Nomba is still processing this checkout. Return to WhatsApp and type track in a moment."
            ),
        )

    if payment.status == Payment.STATUS_SUCCESS:
        return _payment_return_page(
            title="Payment Confirmed",
            message=(
                f"Order {escape(payment.order.checkout_reference)} is paid. "
                "Deli has continued the order in WhatsApp."
            ),
            whatsapp_text="track order",
            auto_redirect=True,
        )

    if payment.status == Payment.STATUS_FAILED:
        return _payment_return_page(
            title="Payment Failed",
            message="Nomba did not approve this payment. Return to WhatsApp and choose payment again.",
            whatsapp_text="cart",
        )

    return _payment_return_page(
        title="Payment Processing",
        message=(
            f"Order {escape(payment.order.checkout_reference)} is still processing. "
            "Return to WhatsApp and type track in a moment."
        ),
        whatsapp_text="track order",
    )


def _payment_return_page(
    title,
    message,
    whatsapp_text="track order",
    auto_redirect=False,
):

    whatsapp_url = ""
    public_number = (
        getattr(settings, "WHATSAPP_PUBLIC_NUMBER", "")
        or getattr(settings, "DELI_DASH_WHATSAPP_NUMBER", "")
    )

    if public_number:
        whatsapp_url = (
            f"https://wa.me/{public_number}?text={quote(whatsapp_text)}"
        )

    redirect_meta = (
        f'<meta http-equiv="refresh" content="3;url={escape(whatsapp_url)}">'
        if auto_redirect and whatsapp_url
        else ""
    )

    button = (
        f'<a class="button" href="{escape(whatsapp_url)}">Return to WhatsApp</a>'
        if whatsapp_url
        else '<p class="hint">Open WhatsApp and type <strong>track</strong>.</p>'
    )

    return HttpResponse(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {redirect_meta}
  <title>{escape(title)} | Deli</title>
  <style>
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      background: #0b0b0c;
      color: #ffffff;
      font-family: Inter, Arial, sans-serif;
    }}
    main {{
      width: min(92vw, 480px);
      padding: 36px;
      border: 1px solid rgba(255,255,255,.12);
      border-radius: 24px;
      background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03));
      box-shadow: 0 24px 80px rgba(0,0,0,.35);
    }}
    .brand {{
      color: #ff2d2d;
      font-size: 14px;
      font-weight: 800;
      letter-spacing: .12em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 14px 0;
      font-size: 34px;
      line-height: 1;
    }}
    p {{
      color: #e7e7e7;
      line-height: 1.65;
      margin: 0 0 24px;
    }}
    .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 48px;
      padding: 0 22px;
      border-radius: 999px;
      background: #ff2d2d;
      color: #fff;
      text-decoration: none;
      font-weight: 800;
    }}
    .hint {{
      color: #bdbdbd;
      margin-bottom: 0;
    }}
  </style>
</head>
<body>
  <main>
    <div class="brand">Deli checkout</div>
    <h1>{escape(title)}</h1>
    <p>{message}</p>
    {button}
  </main>
</body>
</html>"""
    )


@csrf_exempt
def nomba_webhook(request):

    if request.method != "POST":
        return JsonResponse(
            {
                "status": "method_not_allowed",
            },
            status=405,
        )

    body = request.body

    try:
        payload = json.loads(body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse(
            {
                "status": "invalid_json",
            },
            status=400,
        )

    if not PaymentService.verify_webhook(
        body,
        request.headers,
        payload=payload,
    ):
        return JsonResponse(
            {
                "status": "invalid_signature",
            },
            status=401,
        )

    request_id = PaymentService.request_id(payload)
    event_type = PaymentService.event_type(payload)

    try:
        NombaWebhookEvent.objects.create(
            request_id=request_id,
            event_type=event_type,
            payload=payload,
        )
    except IntegrityError:
        return JsonResponse(
            {
                "status": "duplicate",
            }
        )

    try:
        PaymentService.handle_event(payload)
    except Exception as exc:
        logger.exception("Nomba webhook processing failed: %s", exc)
        return JsonResponse(
            {
                "status": "stored_with_processing_error",
            }
        )

    return JsonResponse(
        {
            "status": "processed",
        }
    )
