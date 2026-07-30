# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: DB Analytics MCP Server - Safe Database Queries for AI
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/db-mcp-server
# =============================================================================
import os

from db_analytics_mcp.safety import SafetyConfig


def load_safety_config() -> SafetyConfig:
    """Load safety configuration from environment variables.

    Reads DB_MCP_MAX_ROWS, DB_MCP_TIMEOUT, and DB_MCP_MAX_QUERY_LENGTH
    from the environment, falling back to SafetyConfig defaults.
    """
    return SafetyConfig(
        max_rows=int(os.environ.get("DB_MCP_MAX_ROWS", "500")),
        timeout_seconds=float(os.environ.get("DB_MCP_TIMEOUT", "10.0")),
        max_query_length=int(
            os.environ.get("DB_MCP_MAX_QUERY_LENGTH", "2000")
        ),
    )
