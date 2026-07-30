# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: Firefly-AEM Pipeline - Generative Asset Automation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/adobe/firefly-aem-pipeline
# =============================================================================
"""Orchestrates Firefly image generation and AEM upload as a batch pipeline."""

import logging
from dataclasses import dataclass

import httpx

from firefly_aem.auth import TokenManager
from firefly_aem.generate import RateLimiter, generate_images
from firefly_aem.upload import upload_to_aem

logger = logging.getLogger(__name__)


@dataclass
class AssetJob:
    """Defines a single image generation and upload task.

    Attributes:
        prompt: Text prompt for Firefly image generation.
        folder: AEM DAM folder path for the uploaded asset.
        name_prefix: File name prefix for generated variants.
        width: Output image width in pixels.
        height: Output image height in pixels.
        num_variations: Number of image variants to produce.
    """

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
    """Execute generation pipeline. Returns list of AEM asset paths created.

    Args:
        jobs: List of asset generation jobs to process.
        token_manager: Manages Adobe IMS token lifecycle.
        client_id: Adobe Developer Console client ID.
        aem_host: AEM instance base URL.
        aem_token: AEM authentication token.
        rate_limiter: Optional rate limiter instance for Firefly API calls.

    Returns:
        List of DAM paths for successfully uploaded assets.
    """
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
            logger.error("Generation failed for '%s': %s", job.name_prefix, e)
            continue

        async with httpx.AsyncClient() as http:
            for i, url in enumerate(image_urls):
                try:
                    resp = await http.get(url, timeout=30.0)
                    resp.raise_for_status()
                except httpx.HTTPError as e:
                    logger.warning(
                        "Failed to download variant %d: %s", i + 1, e
                    )
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
                    logger.info("Uploaded: %s/%s", job.folder, file_name)
                except Exception as e:
                    logger.error("Upload failed for %s: %s", file_name, e)

    return created_paths
