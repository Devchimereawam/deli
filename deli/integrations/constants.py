from django.conf import settings


NOMBA_SANDBOX_URL = "https://sandbox.nomba.com/v1"

NOMBA_PRODUCTION_URL = "https://api.nomba.com/v1"


def get_nomba_base_url() -> str:
    """
    Returns the configured Nomba base URL.

    Defaults to Sandbox for safety.
    """

    base_url = getattr(
        settings,
        "NOMBA_BASE_URL",
        NOMBA_SANDBOX_URL,
    ).rstrip("/")

    if not base_url.endswith("/v1"):
        base_url = f"{base_url}/v1"

    return base_url
