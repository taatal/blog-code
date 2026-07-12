import asyncio
import logging
from dataclasses import dataclass

import httpx

from firefly_aem.auth import TokenManager
from firefly_aem.generate import RateLimiter, generate_images
from firefly_aem.upload import upload_to_aem

logger = logging.getLogger(__name__)


@dataclass
class AssetJob:
    prompt: str
    folder: str
    name_prefix: str
    width: int = 2048
    height: int = 2048
    num_variations: int = 4


async def run_pipeline(
    jobs: list[AssetJob],
    token_manager: TokenManager,
    client_id: str,
    aem_host: str,
    aem_token: str,
    rate_limiter: RateLimiter | None = None,
) -> list[str]:
    """Execute generation pipeline. Returns list of AEM asset paths created."""
    if rate_limiter is None:
        rate_limiter = RateLimiter()

    created_paths: list[str] = []

    for job in jobs:
        await rate_limiter.acquire()

        try:
            image_urls = await generate_images(
                token_manager=token_manager,
                client_id=client_id,
                prompt=job.prompt,
                width=job.width,
                height=job.height,
                num_variations=job.num_variations,
            )
        except Exception as e:
            logger.error(f"Generation failed for '{job.name_prefix}': {e}")
            continue

        async with httpx.AsyncClient() as http:
            for i, url in enumerate(image_urls):
                try:
                    resp = await http.get(url, timeout=30.0)
                    resp.raise_for_status()
                except httpx.HTTPError as e:
                    logger.warning(f"Failed to download variant {i+1}: {e}")
                    continue

                image_bytes = resp.content
                file_name = f"{job.name_prefix}-v{i+1}.png"

                try:
                    await upload_to_aem(
                        aem_host=aem_host,
                        aem_token=aem_token,
                        folder_path=job.folder,
                        file_name=file_name,
                        image_bytes=image_bytes,
                    )
                    created_paths.append(f"/content/dam/{job.folder}/{file_name}")
                    logger.info(f"Uploaded: {job.folder}/{file_name}")
                except Exception as e:
                    logger.error(f"Upload failed for {file_name}: {e}")

    return created_paths
