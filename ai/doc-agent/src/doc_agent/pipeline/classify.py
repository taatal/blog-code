import json
import logging

from doc_agent.llm import create_message
from doc_agent.pipeline.retry import call_with_retry

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """Classify this document into exactly one category.

Categories:
- invoice: A bill requesting payment for goods or services
- purchase_order: A buyer's request to a vendor for goods/services
- contract: A legal agreement between parties
- receipt: Proof of payment already made
- unknown: Does not fit any category above

Respond with a JSON object: {{"category": "...", "confidence": 0.0-1.0, "reasoning": "..."}}

Document text (first 3000 characters):
{text}"""


def parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
    return json.loads(text)


def classify_document(doc: dict) -> dict:
    text_preview = doc["full_text"][:3000]

    def _call():
        response = create_message(
            model="claude-sonnet-4-6-20250514",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": CLASSIFICATION_PROMPT.format(text=text_preview),
            }],
        )
        return parse_json(response.text)

    result = call_with_retry(_call)

    if result["confidence"] < 0.7:
        result = _classify_with_full_context(doc)

    return result


def _classify_with_full_context(doc: dict) -> dict:
    full_text = doc["full_text"][:8000]

    def _call():
        response = create_message(
            model="claude-sonnet-4-6-20250514",
            max_tokens=200,
            messages=[{
                "role": "user",
                "content": CLASSIFICATION_PROMPT.format(text=full_text),
            }],
        )
        return parse_json(response.text)

    return call_with_retry(_call)
