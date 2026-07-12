import time

import httpx

IMS_TOKEN_URL = "https://ims-na1.adobelogin.com/ims/token/v3"


async def get_access_token(client_id: str, client_secret: str, scopes: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            IMS_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": scopes,
            },
        )
        response.raise_for_status()
        return response.json()["access_token"]


class TokenManager:
    """Caches OAuth tokens and refreshes 1 hour before expiry."""

    def __init__(self, client_id: str, client_secret: str, scopes: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._scopes = scopes
        self._token: str | None = None
        self._expires_at: float = 0

    async def get_token(self) -> str:
        if self._token and time.time() < self._expires_at:
            return self._token

        self._token = await get_access_token(
            self._client_id, self._client_secret, self._scopes
        )
        self._expires_at = time.time() + 82800  # Refresh 1h before 24h expiry
        return self._token
