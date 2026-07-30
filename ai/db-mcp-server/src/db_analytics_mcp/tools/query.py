# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: DB Analytics MCP Server - Safe Database Queries for AI
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/db-mcp-server
# =============================================================================
from mcp.server.fastmcp import FastMCP, Context

from db_analytics_mcp.formatting import format_result


def register(mcp: FastMCP) -> None:
    """Register the execute_query tool with the MCP server."""

    @mcp.tool()
    async def execute_query(sql: str, ctx: Context) -> str:
        """Execute a read-only SQL query against the database.

        Only SELECT statements are allowed. Write operations (INSERT, UPDATE,
        DELETE, DROP) are blocked. Results are limited to 500 rows.

        Args:
            sql: A SELECT query to execute against the database.
        """
        db = ctx.request_context.lifespan_context["db"]
        result = await db.execute_safe_query(sql)

        if "error" in result:
            return f"Query blocked or failed: {result['error']}"

        return format_result(
            result["columns"],
            result["rows"],
            result["row_count"],
            result.get("truncated", False),
        )
