import asyncio
import time
from collections import deque

import httpx

from firefly_aem.auth import TokenManager

FIREFLY_BASE = "https://firefly-api.adobe.io"


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

                while self._timestamps and now - self._timestamps[0] > 60:
                    self._timestamps.popleft()

                if len(self._timestamps) < self._rpm:
                    break

                sleep_duration = 60 - (now - self._timestamps[0]) + 0.1
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

    async with httpx.AsyncClient() as client:
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
    """Submit async generation job. Returns job ID for status polling."""
    token = await token_manager.get_token()

    async with httpx.AsyncClient() as client:
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
    """Poll until async job completes. Returns output URLs."""
    token = await token_manager.get_token()
    start = time.time()

    async with httpx.AsyncClient() as client:
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

            await asyncio.sleep(3)

    raise TimeoutError(f"Job {job_id} did not complete within {max_wait}s")
