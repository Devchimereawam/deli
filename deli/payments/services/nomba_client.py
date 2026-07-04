import requests

from django.conf import settings

from integrations.constants import get_nomba_base_url
from integrations.exceptions import APIError
from payments.services.auth_service import NombaAuthService


class NombaClient:

    @classmethod
    def headers(cls):

        token = NombaAuthService.get_access_token()

        return {
            "Authorization": f"Bearer {token}",
            "accountId": settings.NOMBA_ACCOUNT_ID,
            "Content-Type": "application/json",
        }

    @classmethod
    def get(cls, endpoint, params=None):

        response = requests.get(
            f"{get_nomba_base_url()}{endpoint}",
            headers=cls.headers(),
            params=params,
            timeout=30,
        )

        cls._validate(response)

        return response.json()

    @classmethod
    def post(cls, endpoint, payload):

        response = requests.post(
            f"{get_nomba_base_url()}{endpoint}",
            headers=cls.headers(),
            json=payload,
            timeout=30,
        )

        cls._validate(response)

        return response.json()

    @classmethod
    def delete(cls, endpoint):

        response = requests.delete(
            f"{get_nomba_base_url()}{endpoint}",
            headers=cls.headers(),
            timeout=30,
        )

        cls._validate(response)

        return response.json()

    @staticmethod
    def _validate(response):

        if response.ok:
            return

        try:
            message = response.json()
        except Exception:
            message = response.text

        raise APIError(message)