import os

from db_analytics_mcp.safety import SafetyConfig


def load_safety_config() -> SafetyConfig:
    return SafetyConfig(
        max_rows=int(os.environ.get("DB_MCP_MAX_ROWS", "500")),
        timeout_seconds=float(os.environ.get("DB_MCP_TIMEOUT", "10.0")),
        max_query_length=int(os.environ.get("DB_MCP_MAX_QUERY_LENGTH", "2000")),
    )
