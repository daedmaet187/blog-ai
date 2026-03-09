import hashlib
import hmac
import json
import os
from typing import Any
from urllib import request as urllib_request


class WaylClient:
    def __init__(
        self,
        api_key: str | None = None,
        webhook_secret: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("WAYL_API_KEY", "")
        self.webhook_secret = webhook_secret or os.getenv("WAYL_WEBHOOK_SECRET", "")
        self.base_url = (base_url or os.getenv("WAYL_BASE_URL", "https://api.wayl.io")).rstrip("/")

    def create_deposit_session(self, *, project_id: int, title: str, package: str) -> dict[str, Any]:
        payload = json.dumps(
            {
                "reference": f"project-{project_id}",
                "description": title,
                "metadata": {"project_id": project_id, "package": package, "payment_stage": "deposit"},
            }
        ).encode("utf-8")

        req = urllib_request.Request(
            f"{self.base_url}/v1/deposits/sessions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib_request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    def create_final_payment_session(self, *, project_id: int, title: str, package: str) -> dict[str, Any]:
        payload = json.dumps(
            {
                "reference": f"project-{project_id}-final",
                "description": f"Final payment for {title}",
                "metadata": {"project_id": project_id, "package": package, "payment_stage": "final"},
            }
        ).encode("utf-8")

        req = urllib_request.Request(
            f"{self.base_url}/v1/final-payments/sessions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib_request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        if not self.webhook_secret or not signature:
            return False
        digest = hmac.new(self.webhook_secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(digest, signature)

    @staticmethod
    def decode_event(payload: bytes) -> dict[str, Any]:
        return json.loads(payload.decode("utf-8"))
