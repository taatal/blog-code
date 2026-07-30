# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: Firefly-AEM Pipeline - Generative Asset Automation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/adobe/firefly-aem-pipeline
# =============================================================================
"""Adobe Firefly image generation with sync and async APIs."""

import asyncio
import time
from collections import deque

import httpx

from firefly_aem.auth import TokenManager

FIREFLY_BASE = "https://firefly-api.adobe.io"
_USER_AGENT = "taatal-firefly-aem/0.1.0 (digital.taatal.com)"

_RATE_WINDOW_SECONDS = 60
_SLEEP_BUFFER = 0.1
_POLL_INTERVAL_SECONDS = 3


class RateLimiter:
    """Enforces Adobe's published rate limit: 4 requests per minute (default)."""

    def __init__(self, rpm: int = 4):
        self._rpm = rpm
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            while True:
                now = time.time()

                while (
                    self._timestamps
                    and now - self._timestamps[0] > _RATE_WINDOW_SECONDS
                ):
                    self._timestamps.popleft()

                if len(self._timestamps) < self._rpm:
                    break

                sleep_duration = (
                    _RATE_WINDOW_SECONDS
                    - (now - self._timestamps[0])
                    + _SLEEP_BUFFER
                )
                await asyncio.sleep(sleep_duration)

            self._timestamps.append(time.time())


async def generate_images(
    token_manager: TokenManager,
    client_id: str,
    prompt: str,
    width: int = 2048,
    height: int = 2048,
    num_variations: int = 4,
) -> list[str]:
    """Generate images via Firefly sync API. Returns presigned output URLs."""
    token = await token_manager.get_token()

    async with httpx.AsyncClient(headers={"User-Agent": _USER_AGENT}) as client:
        response = await client.post(
            f"{FIREFLY_BASE}/v3/images/generate",
            headers={
                "Authorization": f"Bearer {token}",
                "x-api-key": client_id,
                "Content-Type": "application/json",
            },
            json={
                "prompt": prompt,
                "size": {"width": width, "height": height},
                "numVariations": num_variations,
            },
            timeout=60.0,
        )
        response.raise_for_status()
        outputs = response.json()["outputs"]
        return [output["image"]["url"] for output in outputs]


async def generate_images_async(
    token_manager: TokenManager,
    client_id: str,
    prompt: str,
    width: int = 2048,
    height: int = 2048,
    num_variations: int = 4,
) -> str:
    """Submit async generation job. Returns job ID for status polling.

    Args:
        token_manager: Manages Adobe IMS token lifecycle.
        client_id: Adobe Developer Console client ID.
        prompt: Text prompt for image generation.
        width: Output image width in pixels.
        height: Output image height in pixels.
        num_variations: Number of image variants to produce.

    Returns:
        The job ID string for polling via poll_job_status.
    """
    token = await token_manager.get_token()

    async with httpx.AsyncClient(
        headers={"User-Agent": _USER_AGENT}, timeout=60.0
    ) as client:
        response = await client.post(
            f"{FIREFLY_BASE}/v3/images/generate-async",
            headers={
                "Authorization": f"Bearer {token}",
                "x-api-key": client_id,
                "Content-Type": "application/json",
            },
            json={
                "prompt": prompt,
                "size": {"width": width, "height": height},
                "numVariations": num_variations,
            },
        )
        response.raise_for_status()
        return response.json()["jobId"]


async def poll_job_status(
    token_manager: TokenManager,
    client_id: str,
    job_id: str,
    max_wait: int = 120,
) -> list[str]:
    """Poll until async job completes. Returns output URLs.

    Args:
        token_manager: Manages Adobe IMS token lifecycle.
        client_id: Adobe Developer Console client ID.
        job_id: The job ID returned by generate_images_async.
        max_wait: Maximum seconds to wait before raising TimeoutError.

    Returns:
        List of presigned output image URLs.

    Raises:
        RuntimeError: If the generation job reports failure.
        TimeoutError: If the job does not complete within max_wait seconds.
    """
    token = await token_manager.get_token()
    start = time.time()

    async with httpx.AsyncClient(
        headers={"User-Agent": _USER_AGENT}, timeout=60.0
    ) as client:
        while time.time() - start < max_wait:
            response = await client.get(
                f"{FIREFLY_BASE}/v3/status/{job_id}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "x-api-key": client_id,
                },
            )
            response.raise_for_status()
            data = response.json()

            if data["status"] == "succeeded":
                return [out["image"]["url"] for out in data["outputs"]]
            if data["status"] == "failed":
                raise RuntimeError(f"Generation failed: {data}")

            await asyncio.sleep(_POLL_INTERVAL_SECONDS)

    raise TimeoutError(f"Job {job_id} did not complete within {max_wait}s")
