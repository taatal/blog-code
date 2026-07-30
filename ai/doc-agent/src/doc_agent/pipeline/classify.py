# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: Doc-Agent - AI Document Processing Pipeline
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/doc-agent
# =============================================================================
"""Document classification using LLM-based category detection."""

from __future__ import annotations

import json

from doc_agent.llm import create_message
from doc_agent.pipeline.retry import call_with_retry

_PREVIEW_CHAR_LIMIT = 3000
_FULL_CONTEXT_CHAR_LIMIT = 8000
_MIN_CONFIDENCE = 0.7
_CLASSIFICATION_MAX_TOKENS = 200

CLASSIFICATION_PROMPT = """Classify this document into exactly one category.

Categories:
- invoice: A bill requesting payment for goods or services
- purchase_order: A buyer's request to a vendor for goods/services
- contract: A legal agreement between parties
- receipt: Proof of payment already made
- unknown: Does not fit any category above

Respond with a JSON object: {{"category": "...", "confidence": 0.0-1.0, "reasoning": "..."}}

Document text (first {limit} characters):
{text}"""


def parse_json(text: str) -> dict:
    """Parse a JSON string, stripping optional markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text)


def classify_document(doc: dict) -> dict:
    """Classify a document by category using the LLM.

    Args:
        doc: Document dict containing 'full_text' key.

    Returns:
        Dict with 'category', 'confidence', and 'reasoning' keys.
    """
    text_preview = doc["full_text"][:_PREVIEW_CHAR_LIMIT]

    def _call() -> dict:
        response = create_message(
            model="claude-sonnet-4-6-20250514",
            max_tokens=_CLASSIFICATION_MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": CLASSIFICATION_PROMPT.format(
                    text=text_preview, limit=_PREVIEW_CHAR_LIMIT
                ),
            }],
        )
        return parse_json(response.text)

    result = call_with_retry(_call)

    if result["confidence"] < _MIN_CONFIDENCE:
        result = _classify_with_full_context(doc)

    return result


def _classify_with_full_context(doc: dict) -> dict:
    """Re-classify using a larger text window for low-confidence results."""
    full_text = doc["full_text"][:_FULL_CONTEXT_CHAR_LIMIT]

    def _call() -> dict:
        response = create_message(
            model="claude-sonnet-4-6-20250514",
            max_tokens=_CLASSIFICATION_MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": CLASSIFICATION_PROMPT.format(
                    text=full_text, limit=_FULL_CONTEXT_CHAR_LIMIT
                ),
            }],
        )
        return parse_json(response.text)

    return call_with_retry(_call)
