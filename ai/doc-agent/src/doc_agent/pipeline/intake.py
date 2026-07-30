# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: Doc-Agent - AI Document Processing Pipeline
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/doc-agent
# =============================================================================
"""PDF intake: text and table extraction using PyMuPDF."""

from __future__ import annotations

import sys
import io
import fitz
from pathlib import Path


def extract_text(pdf_path: Path) -> dict:
    """Extract text and tables from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Dict with filename, page_count, pages, full_text, and tables.
    """
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        doc = fitz.open(pdf_path)
        pages = []

        for page_num, page in enumerate(doc):
            text = page.get_text()
            tables = _extract_tables(page)

            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "tables": tables,
                "has_tables": len(tables) > 0,
            })

        doc.close()
    finally:
        sys.stdout = old_stdout

    return {
        "filename": pdf_path.name,
        "page_count": len(pages),
        "pages": pages,
        "full_text": "\n\n".join(p["text"] for p in pages),
        "tables": [t for p in pages for t in p["tables"]],
    }


def _extract_tables(page) -> list[str]:
    """Extract tables from a PDF page as markdown strings."""
    tables = page.find_tables()
    extracted = []

    for table in tables:
        df = table.to_pandas()
        extracted.append(df.to_markdown(index=False))

    return extracted
