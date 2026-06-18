import re
from dataclasses import dataclass


BLOCKED_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
    "TRUNCATE", "REPLACE", "GRANT", "REVOKE", "ATTACH",
    "DETACH", "VACUUM", "REINDEX", "PRAGMA",
]

BLOCKED_TABLES = ["sqlite_master", "sqlite_sequence", "sqlite_stat1", "sqlite_stat4"]

ALLOWED_STARTERS = ["SELECT", "WITH", "EXPLAIN"]


@dataclass
class SafetyConfig:
    max_rows: int = 500
    timeout_seconds: float = 10.0
    max_query_length: int = 2000


@dataclass
class ValidationResult:
    safe: bool
    reason: str = ""


def _strip_comments(sql: str) -> str:
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return sql


def _normalize(sql: str) -> str:
    return " ".join(sql.split())


def validate_query(sql: str, config: SafetyConfig = SafetyConfig()) -> ValidationResult:
    if not sql or not sql.strip():
        return ValidationResult(safe=False, reason="Empty query")

    if len(sql) > config.max_query_length:
        return ValidationResult(
            safe=False,
            reason=f"Query exceeds maximum length of {config.max_query_length} characters",
        )

    cleaned = _strip_comments(sql)
    normalized = _normalize(cleaned).strip()

    if not normalized:
        return ValidationResult(safe=False, reason="Query is empty after removing comments")

    upper = normalized.upper()

    first_word = upper.split()[0] if upper.split() else ""
    if first_word not in ALLOWED_STARTERS:
        return ValidationResult(
            safe=False,
            reason=f"Query must start with SELECT, WITH, or EXPLAIN. Got: {first_word}",
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


def enforce_row_limit(sql: str, max_rows: int = 500) -> str:
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
