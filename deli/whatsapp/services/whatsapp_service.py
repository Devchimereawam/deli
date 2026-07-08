import os
import logging
import mimetypes
import requests

BASE_URL = os.getenv("NGROK_URL", "").rstrip("/")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

logger = logging.getLogger(__name__)


class WhatsAppService:

    GRAPH_URL = (
        f"https://graph.facebook.com/v23.0/"
        f"{PHONE_NUMBER_ID}/messages"
    )

    @classmethod
    def send_text(cls, phone, text):

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        body = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text,
            },
        }

        try:
            response = requests.post(
                cls.GRAPH_URL,
                headers=headers,
                json=body,
                timeout=15,
            )
        except requests.RequestException as exc:
            logger.exception("WhatsApp text send failed: %s", exc)
            return None

        print("=" * 60)
        print("STATUS:", response.status_code)
        print("BODY:", response.text)
        print("=" * 60)

        if not response.ok:
            logger.error(
                "WhatsApp text send returned %s: %s",
                response.status_code,
                response.text,
            )
            return None

        return response.json()

    @classmethod
    def request_location(cls, phone):

        return cls.send_text(
            phone,
            """📍 *Set Delivery Location*

Use *Live Location* or *Current Location* if you want restaurants near your exact area, or if you live in a large city with many areas.

To see restaurants across a whole city, simply type the city name.

Examples:
Nsukka
Enugu
Lagos

You can also type a full delivery address if you want us to save that address."""
        )

    @classmethod
    def send_buttons(
        cls,
        phone,
        body_text,
        buttons,
        footer_text="",
    ):

        safe_buttons = list(buttons)[:3]

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        interactive = {
            "type": "button",
            "body": {
                "text": body_text,
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": button_id[:256],
                            "title": title[:20],
                        },
                    }
                    for button_id, title in safe_buttons
                ],
            },
        }

        if footer_text:
            interactive["footer"] = {
                "text": footer_text[:60],
            }

        body = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "interactive",
            "interactive": interactive,
        }

        try:
            response = requests.post(
                cls.GRAPH_URL,
                headers=headers,
                json=body,
                timeout=15,
            )
        except requests.RequestException as exc:
            logger.exception("WhatsApp button send failed: %s", exc)
            return cls._button_fallback(
                phone,
                body_text,
                safe_buttons,
                footer_text,
            )

        print("=" * 60)
        print("BUTTON STATUS:", response.status_code)
        print("BUTTON BODY:", response.text)
        print("=" * 60)

        if not response.ok:
            logger.error(
                "WhatsApp button send returned %s: %s",
                response.status_code,
                response.text,
            )
            return cls._button_fallback(
                phone,
                body_text,
                safe_buttons,
                footer_text,
            )

        return response.json()

    @classmethod
    def _button_fallback(
        cls,
        phone,
        body_text,
        buttons,
        footer_text="",
    ):

        text = body_text

        if buttons:
            text += "\n\n"
            for index, (_, title) in enumerate(
                buttons,
                start=1,
            ):
                text += f"{index}. {title}\n"

        if footer_text:
            text += f"\n{footer_text}"

        return cls.send_text(
            phone,
            text,
        )

    @classmethod
    def send_list(
        cls,
        phone,
        body_text,
        rows,
        button_text="Choose",
        footer_text="",
    ):

        safe_rows = list(rows)[:10]

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        interactive = {
            "type": "list",
            "body": {
                "text": body_text[:1024],
            },
            "action": {
                "button": button_text[:20],
                "sections": [
                    {
                        "title": "Options",
                        "rows": [
                            {
                                "id": str(row_id)[:200],
                                "title": title[:24],
                                "description": description[:72],
                            }
                            for row_id, title, description in safe_rows
                        ],
                    }
                ],
            },
        }

        if footer_text:
            interactive["footer"] = {
                "text": footer_text[:60],
            }

        body = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "interactive",
            "interactive": interactive,
        }

        try:
            response = requests.post(
                cls.GRAPH_URL,
                headers=headers,
                json=body,
                timeout=15,
            )
        except requests.RequestException as exc:
            logger.exception("WhatsApp list send failed: %s", exc)
            return cls._list_fallback(
                phone,
                body_text,
                safe_rows,
                footer_text,
            )

        print("=" * 60)
        print("LIST STATUS:", response.status_code)
        print("LIST BODY:", response.text)
        print("=" * 60)

        if not response.ok:
            logger.error(
                "WhatsApp list send returned %s: %s",
                response.status_code,
                response.text,
            )
            return cls._list_fallback(
                phone,
                body_text,
                safe_rows,
                footer_text,
            )

        return response.json()

    @classmethod
    def _list_fallback(
        cls,
        phone,
        body_text,
        rows,
        footer_text="",
    ):

        text = body_text

        if rows:
            text += "\n\n"
            for row_id, title, description in rows:
                text += f"{row_id}. {title}"
                if description:
                    text += f"\n   {description}"
                text += "\n\n"

        if footer_text:
            text += f"\n{footer_text}"

        return cls.send_text(
            phone,
            text,
        )

    @classmethod
    def send_url_button(
        cls,
        phone,
        body_text,
        button_text,
        url,
        fallback_text=None,
    ):

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        body = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "interactive",
            "interactive": {
                "type": "cta_url",
                "body": {
                    "text": body_text[:1024],
                },
                "action": {
                    "name": "cta_url",
                    "parameters": {
                        "display_text": button_text[:20],
                        "url": url,
                    },
                },
            },
        }

        try:
            response = requests.post(
                cls.GRAPH_URL,
                headers=headers,
                json=body,
                timeout=15,
            )
        except requests.RequestException as exc:
            logger.exception("WhatsApp URL button send failed: %s", exc)
            return cls.send_text(
                phone,
                fallback_text or f"{body_text}\n\n{button_text}: {url}",
            )

        print("=" * 60)
        print("URL BUTTON STATUS:", response.status_code)
        print("URL BUTTON BODY:", response.text)
        print("=" * 60)

        if not response.ok:
            logger.error(
                "WhatsApp URL button send returned %s: %s",
                response.status_code,
                response.text,
            )
            return cls.send_text(
                phone,
                fallback_text or f"{body_text}\n\n{button_text}: {url}",
            )

        return response.json()
        
    @classmethod
    def send_image(cls, phone, image_url, caption=""):

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        body = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": caption,
            },
        }

        try:
            response = requests.post(
                cls.GRAPH_URL,
                headers=headers,
                json=body,
                timeout=15,
            )
        except requests.RequestException as exc:
            logger.exception("WhatsApp image send failed: %s", exc)
            return None

        print("=" * 60)
        print("IMAGE STATUS:", response.status_code)
        print("IMAGE BODY:", response.text)
        print("=" * 60)

        if not response.ok:
            logger.error(
                "WhatsApp image send returned %s: %s",
                response.status_code,
                response.text,
            )
            return None

        return response.json()

    @classmethod
    def send_image_file(cls, phone, file_path, caption=""):

        media_id = cls._upload_media(file_path)

        if not media_id:
            return cls.send_text(
                phone,
                caption,
            )

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        body = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "image",
            "image": {
                "id": media_id,
                "caption": caption,
            },
        }

        try:
            response = requests.post(
                cls.GRAPH_URL,
                headers=headers,
                json=body,
                timeout=15,
            )
        except requests.RequestException as exc:
            logger.exception("WhatsApp uploaded image send failed: %s", exc)
            return cls.send_text(
                phone,
                caption,
            )

        print("=" * 60)
        print("UPLOADED IMAGE STATUS:", response.status_code)
        print("UPLOADED IMAGE BODY:", response.text)
        print("=" * 60)

        if not response.ok:
            logger.error(
                "WhatsApp uploaded image send returned %s: %s",
                response.status_code,
                response.text,
            )
            return cls.send_text(
                phone,
                caption,
            )

        return response.json()

    @classmethod
    def send_image_field(cls, phone, image_field, caption=""):

        if not image_field:
            return cls.send_text(phone, caption)

        try:
            return cls.send_image_file(
                phone,
                image_field.path,
                caption,
            )
        except (NotImplementedError, ValueError, OSError):
            image_url = f"{BASE_URL}{image_field.url}" if BASE_URL else ""
            if image_url:
                return cls.send_image(
                    phone,
                    image_url,
                    caption,
                )
            return cls.send_text(phone, caption)

    @classmethod
    def send_image_buttons(
        cls,
        phone,
        image_field,
        body_text,
        buttons,
        footer_text="",
    ):

        if not image_field:
            return cls.send_buttons(
                phone,
                body_text,
                buttons,
                footer_text,
            )

        try:
            media_id = cls._upload_media(image_field.path)
        except (NotImplementedError, ValueError, OSError):
            media_id = ""

        if not media_id:
            return cls._image_button_fallback(
                phone,
                image_field,
                body_text,
                buttons,
                footer_text,
            )

        safe_buttons = list(buttons)[:3]

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json",
        }

        interactive = {
            "type": "button",
            "header": {
                "type": "image",
                "image": {
                    "id": media_id,
                },
            },
            "body": {
                "text": body_text[:1024],
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": button_id[:256],
                            "title": title[:20],
                        },
                    }
                    for button_id, title in safe_buttons
                ],
            },
        }

        if footer_text:
            interactive["footer"] = {
                "text": footer_text[:60],
            }

        body = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "interactive",
            "interactive": interactive,
        }

        try:
            response = requests.post(
                cls.GRAPH_URL,
                headers=headers,
                json=body,
                timeout=15,
            )
        except requests.RequestException as exc:
            logger.exception("WhatsApp image button send failed: %s", exc)
            return cls._image_button_fallback(
                phone,
                image_field,
                body_text,
                safe_buttons,
                footer_text,
            )

        print("=" * 60)
        print("IMAGE BUTTON STATUS:", response.status_code)
        print("IMAGE BUTTON BODY:", response.text)
        print("=" * 60)

        if not response.ok:
            logger.error(
                "WhatsApp image button send returned %s: %s",
                response.status_code,
                response.text,
            )
            return cls._image_button_fallback(
                phone,
                image_field,
                body_text,
                safe_buttons,
                footer_text,
            )

        return response.json()

    @classmethod
    def _image_button_fallback(
        cls,
        phone,
        image_field,
        body_text,
        buttons,
        footer_text="",
    ):

        cls.send_image_field(
            phone,
            image_field,
            body_text,
        )

        return cls.send_buttons(
            phone,
            "Choose an option:",
            buttons,
            footer_text,
        )

    @classmethod
    def _upload_media(cls, file_path):

        upload_url = (
            f"https://graph.facebook.com/v23.0/"
            f"{PHONE_NUMBER_ID}/media"
        )
        mime_type = (
            mimetypes.guess_type(file_path)[0]
            or "image/jpeg"
        )

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
        }

        try:
            with open(file_path, "rb") as media_file:
                response = requests.post(
                    upload_url,
                    headers=headers,
                    data={
                        "messaging_product": "whatsapp",
                    },
                    files={
                        "file": (
                            os.path.basename(file_path),
                            media_file,
                            mime_type,
                        ),
                    },
                    timeout=30,
                )
        except OSError as exc:
            logger.exception("WhatsApp media file open failed: %s", exc)
            return ""
        except requests.RequestException as exc:
            logger.exception("WhatsApp media upload failed: %s", exc)
            return ""

        print("=" * 60)
        print("MEDIA UPLOAD STATUS:", response.status_code)
        print("MEDIA UPLOAD BODY:", response.text)
        print("=" * 60)

        if not response.ok:
            logger.error(
                "WhatsApp media upload returned %s: %s",
                response.status_code,
                response.text,
            )
            return ""

        return response.json().get("id", "")
