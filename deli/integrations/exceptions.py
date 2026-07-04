class NombaError(Exception):
    """Base Nomba exception."""


class AuthenticationError(NombaError):
    """OAuth authentication failed."""


class CheckoutError(NombaError):
    """Checkout creation failed."""


class TransferError(NombaError):
    """Transfer failed."""


class WebhookVerificationError(NombaError):
    """Invalid webhook signature."""


class APIError(NombaError):
    """Unexpected API response."""