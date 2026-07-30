# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: DB Analytics MCP Server - Safe Database Queries for AI
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/db-mcp-server
# =============================================================================
from mcp.server.fastmcp import FastMCP, Context


def register(mcp: FastMCP) -> None:
    """Register the data dictionary resource with the MCP server."""

    @mcp.tool()
    async def get_data_dictionary(ctx: Context) -> str:
        """Get the complete data dictionary for the connected database.

        Returns table names, column types, nullable flags, primary keys,
        and foreign key relationships. Auto-generated from the live schema.
        """
        db = ctx.request_context.lifespan_context["db"]
        return await db.generate_data_dictionary()
