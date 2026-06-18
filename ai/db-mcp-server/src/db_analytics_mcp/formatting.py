from typing import Any


def format_table(columns: list[str], rows: list[dict], max_col_width: int = 30) -> str:
    if not rows:
        return "No results returned."

    col_widths = {col: min(max(len(col), max(len(str(row.get(col, ""))) for row in rows)), max_col_width) for col in columns}

    header = " | ".join(col.ljust(col_widths[col]) for col in columns)
    separator = "-|-".join("-" * col_widths[col] for col in columns)
    body = "\n".join(
        " | ".join(str(row.get(col, ""))[:max_col_width].ljust(col_widths[col]) for col in columns)
        for row in rows
    )

    return f"{header}\n{separator}\n{body}"


def format_result(columns: list[str], rows: list[dict], row_count: int, truncated: bool = False) -> str:
    output = format_table(columns, rows)
    footer = f"\n\n({row_count} row{'s' if row_count != 1 else ''} returned"
    if truncated:
        footer += ", results truncated to row limit"
    footer += ")"
    return output + footer


def format_key_value(data: dict[str, Any]) -> str:
    max_key_len = max(len(str(k)) for k in data) if data else 0
    lines = []
    for key, value in data.items():
        lines.append(f"{str(key):<{max_key_len + 2}}{value}")
    return "\n".join(lines)
