# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: DB Analytics MCP Server - Safe Database Queries for AI
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/db-mcp-server
# =============================================================================
import re
from dataclasses import dataclass


BLOCKED_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "GRANT", "REVOKE", "ATTACH",
    "DETACH", "VACUUM", "REINDEX", "PRAGMA",
]

BLOCKED_TABLES = [
    "sqlite_master", "sqlite_sequence",
    "sqlite_stat1", "sqlite_stat4",
]

ALLOWED_STARTERS = ["SELECT", "WITH", "EXPLAIN"]

_DEFAULT_MAX_ROWS = 500


@dataclass
class SafetyConfig:
    """Configuration for query safety constraints.

    Attributes:
        max_rows: Maximum number of rows a query may return.
        timeout_seconds: Query execution timeout in seconds.
        max_query_length: Maximum allowed SQL string length.
    """

    max_rows: int = _DEFAULT_MAX_ROWS
    timeout_seconds: float = 10.0
    max_query_length: int = 2000


@dataclass
class ValidationResult:
    """Result of a query safety validation check.

    Attributes:
        safe: Whether the query passed all checks.
        reason: Explanation when the query is blocked.
    """

    safe: bool
    reason: str = ""


def _strip_comments(sql: str) -> str:
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql


def _normalize(sql: str) -> str:
    return " ".join(sql.split())


def validate_query(
    sql: str, config: SafetyConfig = SafetyConfig()
) -> ValidationResult:
    """Validate a SQL query against safety rules.

    Checks for empty queries, length limits, allowed statement types,
    blocked keywords, and access to system tables.

    Args:
        sql: The raw SQL string to validate.
        config: Safety configuration with limits.

    Returns:
        A ValidationResult indicating whether the query is safe.
    """
    if not sql or not sql.strip():
        return ValidationResult(safe=False, reason="Empty query")

    if len(sql) > config.max_query_length:
        return ValidationResult(
            safe=False,
            reason=(
                f"Query exceeds maximum length of "
                f"{config.max_query_length} characters"
            ),
        )

    cleaned = _strip_comments(sql)
    normalized = _normalize(cleaned).strip()

    if not normalized:
        return ValidationResult(
            safe=False,
            reason="Query is empty after removing comments",
        )

    upper = normalized.upper()

    first_word = upper.split()[0] if upper.split() else ""
    if first_word not in ALLOWED_STARTERS:
        return ValidationResult(
            safe=False,
            reason=(
                f"Query must start with SELECT, WITH, or EXPLAIN. "
                f"Got: {first_word}"
            ),
        )

    for keyword in BLOCKED_KEYWORDS:
        pattern = rf"\b{keyword}\b"
        if re.search(pattern, upper):
            if keyword == "REPLACE" and "REPLACE(" in upper:
                continue
            return ValidationResult(
                safe=False,
                reason=f"Blocked keyword detected: {keyword}",
            )

    for table in BLOCKED_TABLES:
        if table.lower() in normalized.lower():
            return ValidationResult(
                safe=False,
                reason=f"Access to system table blocked: {table}",
            )

    return ValidationResult(safe=True)


def enforce_row_limit(
    sql: str, max_rows: int = _DEFAULT_MAX_ROWS
) -> str:
    """Ensure the query has a LIMIT clause within the allowed maximum.

    If the query already contains a LIMIT higher than max_rows, it is
    reduced. If no LIMIT exists, one is appended.

    Args:
        sql: The SQL query string.
        max_rows: Maximum allowed row count.

    Returns:
        The SQL string with an appropriate LIMIT clause.
    """
    upper = sql.strip().upper()

    limit_match = re.search(r"\bLIMIT\s+(\d+)", upper)
    if limit_match:
        existing_limit = int(limit_match.group(1))
        if existing_limit > max_rows:
            sql = re.sub(
                r"\bLIMIT\s+\d+",
                f"LIMIT {max_rows}",
                sql,
                flags=re.IGNORECASE,
            )
        return sql

    sql = sql.rstrip().rstrip(";")
    return f"{sql} LIMIT {max_rows}"
