from .handlers.text import TextHandler
from .handlers.location import LocationHandler
from .handlers.menu import MenuHandler
from .handlers.restaurant import RestaurantHandler
from .handlers.checkout import CheckoutHandler
from .handlers.unsupported import UnsupportedHandler


class WhatsAppBot:

    HANDLERS = {
        "text": TextHandler(),
        "location": LocationHandler(),
        "interactive": UnsupportedHandler(),
        "button": UnsupportedHandler(),
        "image": UnsupportedHandler(),
        "document": UnsupportedHandler(),
        "audio": UnsupportedHandler(),
        "video": UnsupportedHandler(),
        "sticker": UnsupportedHandler(),
    }

    def process(self, phone, message_type, payload):

        handler = self.HANDLERS.get(
            message_type,
            UnsupportedHandler(),
        )

        return handler.handle(phone, payload)