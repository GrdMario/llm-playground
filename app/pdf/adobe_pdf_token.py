import time

import httpx
from pydantic import BaseModel, Field

from .logger import logger


class AccessToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    set_ts: int = Field(default_factory=lambda: int(time.time()))

    def has_expired(self) -> bool:
        return int(time.time()) > self.set_ts + int(self.expires_in) - 60


class AdobePDFServiceToken:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._token: AccessToken | None = None

    @property
    def token(self) -> str:
        self._refresh()
        return self._token.access_token

    def _refresh(self):
        if self._token and not self._token.has_expired():
            return

        logger.info("[ADOBE-PDF-SERVICE] Refreshing token...")
        with httpx.Client(verify=False, follow_redirects=False) as client:
            res = client.post(
                url="https://pdf-services.adobe.io/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "client_id": self._client_id,
                    "client_secret": self._client_secret,
                },
            )

            self._token = AccessToken(**res.json())
