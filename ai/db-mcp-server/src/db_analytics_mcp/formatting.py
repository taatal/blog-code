# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: DB Analytics MCP Server - Safe Database Queries for AI
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/db-mcp-server
# =============================================================================
from typing import Any

_MAX_COL_WIDTH = 30


def format_table(
    columns: list[str],
    rows: list[dict],
    max_col_width: int = _MAX_COL_WIDTH,
) -> str:
    """Format query results as an aligned plain-text table.

    Args:
        columns: Column header names.
        rows: List of row dicts keyed by column name.
        max_col_width: Maximum display width per column.
    """
    if not rows:
        return "No results returned."

    col_widths = {
        col: min(
            max(
                len(col),
                max(len(str(row.get(col, ""))) for row in rows),
            ),
            max_col_width,
        )
        for col in columns
    }

    header = " | ".join(
        col.ljust(col_widths[col]) for col in columns
    )
    separator = "-|-".join(
        "-" * col_widths[col] for col in columns
    )
    body = "\n".join(
        " | ".join(
            str(row.get(col, ""))[:max_col_width].ljust(
                col_widths[col]
            )
            for col in columns
        )
        for row in rows
    )

    return f"{header}\n{separator}\n{body}"


def format_result(
    columns: list[str],
    rows: list[dict],
    row_count: int,
    truncated: bool = False,
) -> str:
    """Format query results with a footer showing row count.

    Args:
        columns: Column header names.
        rows: List of row dicts keyed by column name.
        row_count: Total number of rows returned.
        truncated: Whether results were limited by the row cap.
    """
    output = format_table(columns, rows)
    footer = (
        f"\n\n({row_count} row{'s' if row_count != 1 else ''} returned"
    )
    if truncated:
        footer += ", results truncated to row limit"
    footer += ")"
    return output + footer


def format_key_value(data: dict[str, Any]) -> str:
    """Format a dict as aligned key-value lines.

    Args:
        data: Mapping of label to value.
    """
    max_key_len = max(len(str(k)) for k in data) if data else 0
    lines = []
    for key, value in data.items():
        lines.append(f"{str(key):<{max_key_len + 2}}{value}")
    return "\n".join(lines)
