# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: Firefly-AEM Pipeline - Generative Asset Automation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/adobe/firefly-aem-pipeline
# =============================================================================
"""Command-line interface for the Firefly-AEM asset generation pipeline."""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from firefly_aem.auth import TokenManager
from firefly_aem.generate import RateLimiter
from firefly_aem.pipeline import AssetJob, run_pipeline

FIREFLY_SCOPES = "openid,AdobeID,firefly_api,ff_apis"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="firefly-aem",
        description="Generate assets with Firefly and upload to AEM Assets",
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to JSON config file with jobs and credentials",
    )
    parser.add_argument(
        "--rpm",
        type=int,
        default=4,
        help="Firefly API rate limit (requests per minute, default: 4)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args()


async def run(args: argparse.Namespace) -> None:
    config = json.loads(args.config.read_text())

    token_manager = TokenManager(
        client_id=config["firefly"]["client_id"],
        client_secret=config["firefly"]["client_secret"],
        scopes=FIREFLY_SCOPES,
    )

    jobs = [
        AssetJob(
            prompt=j["prompt"],
            folder=j["folder"],
            name_prefix=j["name_prefix"],
            width=j.get("width", 2048),
            height=j.get("height", 2048),
            num_variations=j.get("num_variations", 4),
        )
        for j in config["jobs"]
    ]

    rate_limiter = RateLimiter(rpm=args.rpm)

    created = await run_pipeline(
        jobs=jobs,
        token_manager=token_manager,
        client_id=config["firefly"]["client_id"],
        aem_host=config["aem"]["host"],
        aem_token=config["aem"]["token"],
        rate_limiter=rate_limiter,
    )

    print("\nCompleted. %d assets uploaded to AEM:" % len(created))
    for path in created:
        print("  %s" % path)


def _print_banner() -> None:
    """Print the startup banner."""
    from firefly_aem import __version__

    print("\n  Taatal Digital | Firefly-AEM Pipeline v%s" % __version__)
    print("  https://digital.taatal.com\n")


def main() -> None:
    _print_banner()
    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        logging.error("Pipeline failed: %s", e)
        sys.exit(1)
