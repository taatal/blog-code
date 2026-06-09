import logging

from doc_agent.llm import create_message
from doc_agent.schemas import EXTRACTION_TOOLS
from doc_agent.pipeline.retry import call_with_retry
from doc_agent.pipeline.validate import validate_invoice, validate_generic

logger = logging.getLogger(__name__)


def _validate(doc_type: str, data: dict):
    if doc_type == "invoice":
        return validate_invoice(data)
    return validate_generic(data)


def extract_fields(doc: dict, doc_type: str) -> dict:
    tool_name = f"extract_{doc_type}"
    tool = next((t for t in EXTRACTION_TOOLS if t["name"] == tool_name), None)

    if tool is None:
        raise ValueError(f"No extraction schema for document type: {doc_type}")

    tables_text = "\n".join(doc.get("tables", []))

    def _call():
        response = create_message(
            model="claude-sonnet-4-6-20250514",
            max_tokens=4096,
            tools=[tool],
            tool_choice={"type": "tool", "name": tool_name},
            messages=[{
                "role": "user",
                "content": f"""Extract all relevant fields from this {doc_type}.
Be precise with numbers and dates. If a field is not present in the document, omit it.
For line items, extract every row from the itemised table.

Document:
{doc['full_text']}

Tables found in document:
{tables_text}""",
            }],
        )
        return response.tool_input

    return call_with_retry(_call)


def _retry_extraction(doc: dict, doc_type: str, previous: dict, errors: list[str]) -> dict:
    tool_name = f"extract_{doc_type}"
    tool = next(t for t in EXTRACTION_TOOLS if t["name"] == tool_name)

    error_context = "\n".join(f"- {e}" for e in errors)
    tables_text = "\n".join(doc.get("tables", []))

    def _call():
        response = create_message(
            model="claude-sonnet-4-6-20250514",
            max_tokens=4096,
            tools=[tool],
            tool_choice={"type": "tool", "name": tool_name},
            messages=[
                {
                    "role": "user",
                    "content": f"""Extract all relevant fields from this {doc_type}.

Document:
{doc['full_text']}

Tables:
{tables_text}""",
                },
                {
                    "role": "assistant",
                    "content": [{"type": "tool_use", "id": "prev", "name": tool_name, "input": previous}],
                },
                {
                    "role": "user",
                    "content": [{"type": "tool_result", "tool_use_id": "prev", "content": f"""Validation failed with these errors:
{error_context}

Please re-extract, paying careful attention to the specific fields mentioned in the errors. Double-check all numbers against the original document."""}],
                },
            ],
        )
        return response.tool_input

    return call_with_retry(_call)


def extract_with_retry(doc: dict, doc_type: str, max_retries: int = 2) -> dict:
    result = extract_fields(doc, doc_type)

    for attempt in range(max_retries):
        validation = _validate(doc_type, result)

        if validation.valid:
            return {"data": result, "validation": validation, "attempts": attempt + 1}

        logger.info(f"Validation failed (attempt {attempt + 1}): {validation.errors}")
        result = _retry_extraction(doc, doc_type, result, validation.errors)

    validation = _validate(doc_type, result)

    if validation.valid:
        return {"data": result, "validation": validation, "attempts": max_retries + 1}

    return {
        "data": result,
        "validation": validation,
        "attempts": max_retries + 1,
        "needs_review": True,
    }
