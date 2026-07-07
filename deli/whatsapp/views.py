import json
import logging
import os
from datetime import datetime, timezone as datetime_timezone

from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .bot import WhatsAppBot
from .models import ProcessedMessage
from orders.services.order_service import OrderService

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

bot = WhatsAppBot()
logger = logging.getLogger(__name__)


@csrf_exempt
def webhook(request):
    """
    WhatsApp Cloud API Webhook

    GET  -> Meta verification
    POST -> Incoming messages
    """

    # ---------------------------------------
    # Verify Webhook
    # ---------------------------------------

    if request.method == "GET":

        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if (
            mode == "subscribe"
            and token == VERIFY_TOKEN
        ):
            return HttpResponse(challenge)

        return HttpResponse(status=403)

    # ---------------------------------------
    # Incoming Messages
    # ---------------------------------------

    try:

        body = json.loads(request.body)

        print(body)

        OrderService.check_provider_timeouts()

        entry = body.get("entry", [])[0]

        change = entry.get("changes", [])[0]

        value = change.get("value", {})

        # Ignore delivery/read receipts
        if "messages" not in value:
            return JsonResponse({
                "status": "ignored",
            })

        message = value["messages"][0]

        message_id = message["id"]
        message_timestamp = message.get("timestamp")

        if _is_stale_message(message_timestamp):
            return JsonResponse({
                "status": "stale_ignored",
            })

        # Prevent duplicate processing
        try:

            ProcessedMessage.objects.create(
                whatsapp_message_id=message_id,
            )

        except IntegrityError:

            return JsonResponse({
                "status": "duplicate",
            })

        phone = message["from"]

        message_type = message["type"]

        if message_type == "text":

            payload = message["text"]["body"]

        elif message_type == "location":

            payload = message["location"]

        else:

            payload = message

        try:
            bot.process(
                phone=phone,
                message_type=message_type,
                payload=payload,
            )
        except Exception as exc:
            logger.exception("WhatsApp bot processing failed: %s", exc)
            return JsonResponse({
                "status": "received_with_processing_error",
            })

        return JsonResponse({
            "status": "received",
        })

    except Exception as e:

        logger.exception("WhatsApp webhook failed: %s", e)

        return JsonResponse(
            {
                "status": "error",
                "message": str(e),
            },
            status=400,
        )


def _is_stale_message(timestamp):

    if not timestamp:
        return False

    try:
        sent_at = datetime.fromtimestamp(
            int(timestamp),
            tz=datetime_timezone.utc,
        )
    except (TypeError, ValueError, OSError):
        return False

    age = timezone.now() - sent_at

    return age.total_seconds() > (
        settings.WHATSAPP_STALE_MESSAGE_MINUTES * 60
    )
