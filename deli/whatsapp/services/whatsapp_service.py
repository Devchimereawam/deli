import os
import requests

BASE_URL = os.getenv("NGROK_URL", "").rstrip("/")
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")


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

        response = requests.post(
            cls.GRAPH_URL,
            headers=headers,
            json=body,
            timeout=30,
        )

        print("=" * 60)
        print("STATUS:", response.status_code)
        print("BODY:", response.text)
        print("=" * 60)

        response.raise_for_status()

        return response.json()

    @classmethod
    def request_location(cls, phone):

        cls.send_text(
            phone,
            """📍 Please share your delivery location.

Tap the ➕ attachment icon in WhatsApp and share your Live Location or Current Location.:

📍 Location
→ Current Location

If WhatsApp can't determine your location, simply type your delivery address instead.

We'll use this to show nearby restaurants."""
        )
        
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

        response = requests.post(
            cls.GRAPH_URL,
            headers=headers,
            json=body,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()