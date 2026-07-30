# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: Firefly-AEM Pipeline - Generative Asset Automation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/adobe/firefly-aem-pipeline
# =============================================================================
"""Adobe IMS OAuth token management for Firefly API authentication."""

import logging
import time

import httpx

logger = logging.getLogger(__name__)

IMS_TOKEN_URL = "https://ims-na1.adobelogin.com/ims/token/v3"
_USER_AGENT = "taatal-firefly-aem/0.1.0 (digital.taatal.com)"

# 24h token lifetime minus 1h safety margin (in seconds)
_TOKEN_REFRESH_BUFFER = 82800


async def get_access_token(client_id: str, client_secret: str, scopes: str) -> str:
    """Exchange client credentials for an Adobe IMS access token.

    Args:
        client_id: Adobe Developer Console client ID.
        client_secret: Adobe Developer Console client secret.
        scopes: Comma-separated OAuth scopes.

    Returns:
        A valid access token string.
    """
    async with httpx.AsyncClient(headers={"User-Agent": _USER_AGENT}) as client:
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
        self._expires_at = time.time() + _TOKEN_REFRESH_BUFFER
        return self._token
