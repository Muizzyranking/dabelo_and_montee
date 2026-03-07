import hmac
import hashlib
import uuid

import requests
from django.conf import settings


PAYSTACK_SECRET = getattr(
    settings, "PAYSTACK_SECRET_KEY", "sk_test_256b4924684c580b880cf8ebea9903afafc3cb06"
)
PAYSTACK_PUBLIC = getattr(
    settings, "PAYSTACK_PUBLIC_KEY", "pk_test_7feb8c48e16d259fe367b1bde437f72de00ffe65"
)


if not PAYSTACK_SECRET or not PAYSTACK_PUBLIC:
    import warnings

    warnings.warn(
        "PAYSTACK_SECRET_KEY / PAYSTACK_PUBLIC_KEY not set in settings.",
        RuntimeWarning,
        stacklevel=1,
    )


class PaystackService:
    BASE_URL = "https://api.paystack.co"

    @classmethod
    def generate_reference(cls) -> str:
        """Unique payment reference."""
        return f"PAY-{uuid.uuid4().hex[:16].upper()}"

    @classmethod
    def generate_checkout_token(cls) -> str:
        """Returns a 64-char hex token."""
        return uuid.uuid4().hex + uuid.uuid4().hex

    @classmethod
    def verify_checkout_token(
        cls, session_token: str | None, submitted_token: str | None
    ) -> bool:
        if not session_token or not submitted_token:
            return False
        return hmac.compare_digest(session_token, submitted_token)

    @classmethod
    def _headers(cls) -> dict:
        return {
            "Authorization": f"Bearer {PAYSTACK_SECRET}",
            "Content-Type": "application/json",
        }

    @classmethod
    def verify_transaction(cls, reference: str) -> dict:
        try:
            response = requests.get(
                f"{cls.BASE_URL}/transaction/verify/{reference}",
                headers=cls._headers(),
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ValueError(f"Paystack request failed: {exc}") from exc

        body = response.json()

        if not body.get("status"):
            raise ValueError(body.get("message", "Paystack verification failed."))

        return body["data"]

    @classmethod
    def verify_webhook_signature(cls, payload_bytes: bytes, signature: str) -> bool:
        expected = hmac.new(
            PAYSTACK_SECRET.encode(),
            payload_bytes,
            hashlib.sha512,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
