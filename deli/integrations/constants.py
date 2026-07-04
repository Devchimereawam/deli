from django.conf import settings


NOMBA_SANDBOX_URL = "https://sandbox.api.nomba.com/v1"

NOMBA_PRODUCTION_URL = "https://api.nomba.com/v1"


def get_nomba_base_url() -> str:
    """
    Returns the configured Nomba base URL.

    Defaults to Sandbox for safety.
    """

    return getattr(
        settings,
        "NOMBA_BASE_URL",
        NOMBA_SANDBOX_URL,
    )