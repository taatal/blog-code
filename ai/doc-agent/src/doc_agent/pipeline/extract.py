# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: Doc-Agent - AI Document Processing Pipeline
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/doc-agent
# =============================================================================
"""Field extraction from classified documents with validation retry loop."""

from __future__ import annotations

import logging

from doc_agent.llm import create_message
from doc_agent.schemas import EXTRACTION_TOOLS
from doc_agent.pipeline.retry import call_with_retry
from doc_agent.pipeline.validate import validate_invoice, validate_generic

logger = logging.getLogger(__name__)

_EXTRACTION_MAX_TOKENS = 4096


def _validate(doc_type: str, data: dict):
    """Route validation to the appropriate validator by document type."""
    if doc_type == "invoice":
        return validate_invoice(data)
    return validate_generic(data)


def extract_fields(doc: dict, doc_type: str) -> dict:
    """Extract structured fields from a document using tool-use.

    Args:
        doc: Document dict with 'full_text' and optional 'tables'.
        doc_type: Classification category (e.g. 'invoice').

    Returns:
        Dict of extracted fields.
    """
    tool_name = f"extract_{doc_type}"
    tool = next(
        (t for t in EXTRACTION_TOOLS if t["name"] == tool_name), None
    )

    if tool is None:
        raise ValueError(
            f"No extraction schema for document type: {doc_type}"
        )

    tables_text = "\n".join(doc.get("tables", []))

    def _call() -> dict:
        response = create_message(
            model="claude-sonnet-4-6-20250514",
            max_tokens=_EXTRACTION_MAX_TOKENS,
            tools=[tool],
            tool_choice={"type": "tool", "name": tool_name},
            messages=[{
                "role": "user",
                "content": (
                    f"Extract all relevant fields from this"
                    f" {doc_type}.\n"
                    f"Be precise with numbers and dates. "
                    f"If a field is not present in the document,"
                    f" omit it.\n"
                    f"For line items, extract every row from the"
                    f" itemised table.\n\n"
                    f"Document:\n{doc['full_text']}\n\n"
                    f"Tables found in document:\n{tables_text}"
                ),
            }],
        )
        return response.tool_input

    return call_with_retry(_call)


def _retry_extraction(
    doc: dict,
    doc_type: str,
    previous: dict,
    errors: list[str],
) -> dict:
    """Re-extract fields after a validation failure.

    Args:
        doc: Original document dict.
        doc_type: Classification category.
        previous: Previously extracted data that failed validation.
        errors: List of validation error messages.

    Returns:
        Dict of re-extracted fields.
    """
    tool_name = f"extract_{doc_type}"
    tool = next(t for t in EXTRACTION_TOOLS if t["name"] == tool_name)

    error_context = "\n".join(f"- {e}" for e in errors)
    tables_text = "\n".join(doc.get("tables", []))

    def _call() -> dict:
        response = create_message(
            model="claude-sonnet-4-6-20250514",
            max_tokens=_EXTRACTION_MAX_TOKENS,
            tools=[tool],
            tool_choice={"type": "tool", "name": tool_name},
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Extract all relevant fields from this"
                        f" {doc_type}.\n\n"
                        f"Document:\n{doc['full_text']}\n\n"
                        f"Tables:\n{tables_text}"
                    ),
                },
                {
                    "role": "assistant",
                    "content": [{
                        "type": "tool_use",
                        "id": "prev",
                        "name": tool_name,
                        "input": previous,
                    }],
                },
                {
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": "prev",
                        "content": (
                            "Validation failed with these errors:\n"
                            f"{error_context}\n\n"
                            "Please re-extract, paying careful"
                            " attention to the specific fields"
                            " mentioned in the errors. "
                            "Double-check all numbers against the"
                            " original document."
                        ),
                    }],
                },
            ],
        )
        return response.tool_input

    return call_with_retry(_call)


def extract_with_retry(
    doc: dict, doc_type: str, max_retries: int = 2
) -> dict:
    """Extract fields with automatic validation and retry.

    Args:
        doc: Document dict with 'full_text' and optional 'tables'.
        doc_type: Classification category.
        max_retries: Number of retry attempts after initial extraction.

    Returns:
        Dict with 'data', 'validation', 'attempts', and optionally
        'needs_review' keys.
    """
    result = extract_fields(doc, doc_type)

    for attempt in range(max_retries):
        validation = _validate(doc_type, result)

        if validation.valid:
            return {
                "data": result,
                "validation": validation,
                "attempts": attempt + 1,
            }

        logger.info(
            "Validation failed (attempt %d): %s",
            attempt + 1,
            validation.errors,
        )
        result = _retry_extraction(doc, doc_type, result, validation.errors)

    validation = _validate(doc_type, result)

    if validation.valid:
        return {
            "data": result,
            "validation": validation,
            "attempts": max_retries + 1,
        }

    return {
        "data": result,
        "validation": validation,
        "attempts": max_retries + 1,
        "needs_review": True,
    }
