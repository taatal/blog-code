# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: Doc-Agent - AI Document Processing Pipeline
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/doc-agent
# =============================================================================
"""Validation rules for extracted document data."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

_DECIMAL_TOLERANCE = Decimal("0.02")
_MAX_TAX_RATE = 30
_MAX_INVOICE_NUM_LEN = 50


@dataclass
class ValidationResult:
    """Result of a document validation pass."""

    valid: bool
    errors: list[str]
    warnings: list[str]


def validate_invoice(data: dict) -> ValidationResult:
    """Validate extracted invoice data for arithmetic and logical consistency.

    Args:
        data: Extracted invoice fields.

    Returns:
        ValidationResult with any errors or warnings found.
    """
    errors = []
    warnings = []

    if data.get("line_items") and data.get("subtotal"):
        computed_subtotal = sum(
            Decimal(str(item["total"])) for item in data["line_items"]
        )
        stated_subtotal = Decimal(str(data["subtotal"]))

        if abs(computed_subtotal - stated_subtotal) > _DECIMAL_TOLERANCE:
            errors.append(
                f"Line items sum to {computed_subtotal}, "
                f"but stated subtotal is {stated_subtotal}"
            )

    if (
        data.get("subtotal")
        and data.get("tax_amount")
        and data.get("total_amount")
    ):
        expected_total = (
            Decimal(str(data["subtotal"]))
            + Decimal(str(data["tax_amount"]))
        )
        stated_total = Decimal(str(data["total_amount"]))

        if abs(expected_total - stated_total) > _DECIMAL_TOLERANCE:
            errors.append(
                f"Subtotal ({data['subtotal']}) + tax"
                f" ({data['tax_amount']}) "
                f"!= total ({data['total_amount']})"
            )

    if data.get("due_date") and data.get("invoice_date"):
        if data["due_date"] < data["invoice_date"]:
            errors.append("Due date is before invoice date")

    if data.get("tax_rate"):
        rate = data["tax_rate"]
        if rate > _MAX_TAX_RATE:
            warnings.append(f"Unusually high tax rate: {rate}%")
        if rate < 0:
            errors.append(f"Negative tax rate: {rate}%")

    if data.get("invoice_number"):
        inv_num = data["invoice_number"]
        if len(inv_num) > _MAX_INVOICE_NUM_LEN:
            warnings.append(
                f"Unusually long invoice number: {inv_num}"
            )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


def validate_generic(data: dict) -> ValidationResult:
    """Validate a generic extracted document for minimal completeness.

    Args:
        data: Extracted document fields.

    Returns:
        ValidationResult indicating whether enough fields were extracted.
    """
    errors = []
    warnings = []

    non_null_fields = [
        k for k, v in data.items()
        if v is not None and v != "" and v != []
    ]
    if len(non_null_fields) < 2:
        errors.append(
            "Too few fields extracted. Document may not have been"
            " parsed correctly."
        )

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )
