from .base import BaseHandler
from ..services.whatsapp_service import WhatsAppService


class UnsupportedHandler(BaseHandler):

    def handle(self, phone, payload):

        WhatsAppService.send_text(
            phone,
            """❌ Sorry, I can't process that type of message yet.

Please send:

• Text
or
• Your location.

to continue."""
        )