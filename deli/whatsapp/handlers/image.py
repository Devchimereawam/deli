import mimetypes
import os
from uuid import uuid4

import requests
from django.core.files.base import ContentFile

from restaurants.models import MenuItem, Restaurant

from ..services.customer_service import CustomerService
from ..services.whatsapp_service import WhatsAppService
from .base import BaseHandler


ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
GRAPH_VERSION = "v23.0"


class ImageHandler(BaseHandler):

    def handle(self, phone, payload):

        customer, _, _ = CustomerService.get_customer(phone)

        if customer.account_type != customer.ACCOUNT_RESTAURANT:
            WhatsAppService.send_text(
                phone,
                "Images are currently supported for restaurant admins only. Type home to continue.",
            )
            return

        restaurant = self._restaurant_for_customer(customer)

        if not restaurant:
            WhatsAppService.send_text(
                phone,
                "No restaurant profile found for this number. Type home and contact Deli support if this is wrong.",
            )
            return

        image = payload.get("image", payload)
        media_id = image.get("id")
        caption = image.get("caption", "").strip()

        if not media_id:
            WhatsAppService.send_text(
                phone,
                "Could not read that image. Please resend it with a caption.",
            )
            return

        if not caption:
            WhatsAppService.send_text(
                phone,
                'Add a caption: "logo" or "meal ITEM NAME".',
            )
            return

        content, filename = self._download_media(media_id)

        if not content:
            WhatsAppService.send_text(
                phone,
                "Could not download that image from WhatsApp. Please try again.",
            )
            return

        lower = caption.lower()

        if lower == "logo":
            restaurant.logo.save(
                filename,
                ContentFile(content),
                save=True,
            )
            WhatsAppService.send_text(
                phone,
                f"✅ {restaurant.name} logo updated.",
            )
            return

        item_name = caption

        if lower.startswith("meal "):
            item_name = caption[5:].strip()
        elif lower.startswith("item "):
            item_name = caption[5:].strip()
        elif lower.startswith("image "):
            item_name = caption[6:].strip()

        item = (
            MenuItem.objects
            .filter(
                restaurant=restaurant,
                name__icontains=item_name,
            )
            .order_by("name")
            .first()
        )

        if not item:
            WhatsAppService.send_text(
                phone,
                "Meal item not found. Use caption: meal ITEM NAME",
            )
            return

        item.image.save(
            filename,
            ContentFile(content),
            save=True,
        )

        WhatsAppService.send_text(
            phone,
            f"✅ {item.name} image updated.",
        )

    @staticmethod
    def _restaurant_for_customer(customer):

        return Restaurant.objects.filter(
            phone=customer.phone,
        ).first() or Restaurant.objects.filter(
            whatsapp_number=customer.phone,
        ).first()

    @staticmethod
    def _download_media(media_id):

        if not ACCESS_TOKEN:
            return None, ""

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        }

        try:
            metadata = requests.get(
                f"https://graph.facebook.com/{GRAPH_VERSION}/{media_id}",
                headers=headers,
                timeout=15,
            )
            metadata.raise_for_status()
            data = metadata.json()
            media_url = data.get("url")
            mime_type = data.get("mime_type", "image/jpeg")

            if not media_url:
                return None, ""

            media = requests.get(
                media_url,
                headers=headers,
                timeout=30,
            )
            media.raise_for_status()
        except requests.RequestException:
            return None, ""

        extension = mimetypes.guess_extension(mime_type) or ".jpg"

        return media.content, f"whatsapp-{uuid4().hex}{extension}"
