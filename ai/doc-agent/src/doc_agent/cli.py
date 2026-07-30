# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: Doc-Agent - AI Document Processing Pipeline
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/doc-agent
# =============================================================================
"""Command-line interface for the doc-agent pipeline."""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import asdict
from pathlib import Path

from doc_agent.process import process_batch, process_document


def _print_banner() -> None:
    """Print the startup banner."""
    from doc_agent import __version__

    print(f"\n  Taatal Digital | Doc-Agent v{__version__}")
    print("  https://digital.taatal.com\n")


def main() -> None:
    """Parse arguments and run the document processing pipeline."""
    _print_banner()
    parser = argparse.ArgumentParser(
        description="Process PDF documents with AI extraction"
    )
    parser.add_argument(
        "--input", type=Path, help="Directory containing PDF files"
    )
    parser.add_argument(
        "--file", type=Path, help="Single PDF file to process"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results"),
        help="Directory for JSON output",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Number of concurrent workers",
    )
    args = parser.parse_args()

    if not args.input and not args.file:
        parser.error(
            "Provide either --input (directory) or --file (single PDF)"
        )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.file:
        if not args.file.exists():
            parser.error(f"File not found: {args.file}")
        result = process_document(args.file)
        print(json.dumps(asdict(result), indent=2))
    else:
        process_batch(args.input, args.output, max_workers=args.workers)
