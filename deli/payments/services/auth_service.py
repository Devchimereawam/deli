from datetime import timedelta

import requests

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from integrations.constants import get_nomba_base_url
from integrations.exceptions import AuthenticationError


class NombaAuthService:

    TOKEN_KEY = "nomba_access_token"

    TOKEN_EXPIRY_KEY = "nomba_access_token_expiry"

    TOKEN_REFRESH_MINUTES = 55

    @classmethod
    def get_access_token(cls) -> str:

        token = cache.get(cls.TOKEN_KEY)

        expiry = cache.get(cls.TOKEN_EXPIRY_KEY)

        if (
            token
            and expiry
            and expiry > timezone.now()
        ):
            return token

        return cls.issue_token()

    @classmethod
    def issue_token(cls) -> str:

        response = requests.post(
            f"{get_nomba_base_url()}/auth/token/issue",
            headers={
                "Content-Type": "application/json",
                "accountId": settings.NOMBA_ACCOUNT_ID,
            },
            json={
                "grant_type": "client_credentials",
                "client_id": settings.NOMBA_CLIENT_ID,
                "client_secret": settings.NOMBA_CLIENT_SECRET,
            },
            timeout=30,
        )

        if response.status_code != 200:
            raise AuthenticationError(response.text)

        payload = response.json()

        token = payload["data"]["access_token"]

        expiry = timezone.now() + timedelta(
            minutes=cls.TOKEN_REFRESH_MINUTES
        )

        cache.set(
            cls.TOKEN_KEY,
            token,
            timeout=cls.TOKEN_REFRESH_MINUTES * 60,
        )

        cache.set(
            cls.TOKEN_EXPIRY_KEY,
            expiry,
            timeout=cls.TOKEN_REFRESH_MINUTES * 60,
        )

        return token

    @classmethod
    def clear_cache(cls):

        cache.delete(cls.TOKEN_KEY)

        cache.delete(cls.TOKEN_EXPIRY_KEY)