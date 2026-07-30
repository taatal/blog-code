# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: RAG Pipeline - Hybrid Search, Re-Ranking, and Evaluation
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/rag-pipeline
# =============================================================================
"""Stage 1: PDF text extraction and recursive chunking."""

import logging
from pathlib import Path

import fitz

from rag_pipeline.models import Chunk, ChunkMetadata

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 512
DEFAULT_OVERLAP = 64
_SEPARATORS = ["\n\n", "\n", ". ", " "]


def extract_text(pdf_path: Path) -> dict:
    """Extract text from a PDF file, preserving page structure.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Dictionary with filename, page_count, pages list, and full_text.
    """
    with fitz.open(pdf_path) as doc:
        pages = [
            {"page_number": page_num + 1, "text": page.get_text().strip()}
            for page_num, page in enumerate(doc)
        ]

    return {
        "filename": pdf_path.name,
        "page_count": len(pages),
        "pages": pages,
        "full_text": "\n\n".join(p["text"] for p in pages if p["text"]),
    }


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[dict]:
    """Split text into overlapping chunks using recursive character splitting.

    Tries paragraph boundaries first, then line breaks, then sentence
    boundaries, then word boundaries. This preserves semantic coherence.

    Args:
        text: The input text to chunk.
        chunk_size: Maximum number of words per chunk.
        overlap: Number of words to overlap between adjacent chunks.

    Returns:
        List of dicts with 'text' and 'word_count' keys.
    """
    return _recursive_split(text, _SEPARATORS, chunk_size, overlap)


def _recursive_split(
    text: str,
    separators: list[str],
    chunk_size: int,
    overlap: int,
) -> list[dict]:
    """Recursively split text, trying coarse separators before fine ones."""
    stripped = text.strip()
    if not stripped:
        return []

    words = stripped.split()
    if len(words) <= chunk_size:
        return [{"text": stripped, "word_count": len(words)}]

    separator = _find_separator(stripped, separators)
    splits = stripped.split(separator)
    chunks = _merge_splits(splits, separator, chunk_size, overlap)

    remaining_separators = _get_remaining_separators(separator, separators)
    return _subdivide_oversized(chunks, remaining_separators, chunk_size, overlap)


def _find_separator(text: str, separators: list[str]) -> str:
    """Return the first separator present in the text."""
    for sep in separators:
        if sep in text:
            return sep
    return separators[-1]


def _merge_splits(
    splits: list[str],
    separator: str,
    chunk_size: int,
    overlap: int,
) -> list[dict]:
    """Merge text splits into chunks respecting size limits."""
    chunks: list[dict] = []
    current = ""

    for split in splits:
        candidate = f"{current}{separator}{split}".strip() if current else split.strip()

        if len(candidate.split()) > chunk_size and current:
            chunks.append({"text": current.strip(), "word_count": len(current.split())})
            overlap_words = current.split()[-overlap:] if overlap else []
            current = " ".join(overlap_words) + separator + split if overlap_words else split
        else:
            current = candidate

    if current.strip():
        chunks.append({"text": current.strip(), "word_count": len(current.split())})

    return chunks


def _get_remaining_separators(
    current_separator: str,
    separators: list[str],
) -> list[str]:
    """Get separators finer than the current one."""
    if current_separator in separators:
        idx = separators.index(current_separator)
        return separators[idx + 1 :]
    return []


def _subdivide_oversized(
    chunks: list[dict],
    remaining_separators: list[str],
    chunk_size: int,
    overlap: int,
) -> list[dict]:
    """Recursively split any chunks that still exceed the size limit."""
    result: list[dict] = []
    for chunk in chunks:
        if chunk["word_count"] > chunk_size and remaining_separators:
            sub_chunks = _recursive_split(chunk["text"], remaining_separators, chunk_size, overlap)
            result.extend(sub_chunks)
        else:
            result.append(chunk)
    return result


def ingest_pdf(
    pdf_path: Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[Chunk]:
    """Full ingestion pipeline: extract text from PDF and split into chunks.

    Args:
        pdf_path: Path to the PDF file.
        chunk_size: Maximum words per chunk.
        overlap: Word overlap between adjacent chunks.

    Returns:
        List of Chunk objects with metadata.
    """
    doc = extract_text(pdf_path)
    chunks: list[Chunk] = []

    for page in doc["pages"]:
        if not page["text"]:
            continue

        page_chunks = chunk_text(page["text"], chunk_size, overlap)

        for i, chunk in enumerate(page_chunks):
            metadata = ChunkMetadata(
                source=doc["filename"],
                page=page["page_number"],
                chunk_index=i,
            )
            chunks.append(
                Chunk(
                    text=chunk["text"],
                    word_count=chunk["word_count"],
                    metadata=metadata,
                )
            )

    logger.info("Ingested %s: %d chunks", pdf_path.name, len(chunks))
    return chunks
