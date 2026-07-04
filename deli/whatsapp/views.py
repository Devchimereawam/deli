import json
import os

from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .bot import WhatsAppBot
from .models import ProcessedMessage

VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN")

bot = WhatsAppBot()


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

        bot.process(
            phone=phone,
            message_type=message_type,
            payload=payload,
        )

        return JsonResponse({
            "status": "received",
        })

    except Exception as e:

        print(e)

        return JsonResponse(
            {
                "status": "error",
                "message": str(e),
            },
            status=400,
        )