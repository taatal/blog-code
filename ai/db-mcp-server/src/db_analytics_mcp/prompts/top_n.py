# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: DB Analytics MCP Server - Safe Database Queries for AI
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/db-mcp-server
# =============================================================================
from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register the top-N analysis prompt with the MCP server."""

    @mcp.prompt()
    async def top_n_analysis(
        entity: str = "products",
        metric: str = "revenue",
        n: int = 10,
    ) -> str:
        """Rank and analyze the top N entities by a metric.

        Args:
            entity: What to rank. Options: products, customers,
                categories.
            metric: Ranking metric. Options: revenue, orders, quantity.
            n: How many to return.
        """
        return (
            f"Find and analyze the top {n} {entity} "
            f"by {metric}.\n\n"
            "Use the database tools to:\n"
            f"1. Query the top {n} {entity} ranked by {metric}\n"
            "2. Calculate each item's percentage contribution "
            "to the total\n"
            "3. Identify concentration (does the top 20% account "
            f"for 80% of {metric}?)\n"
            "4. Compare the top performer to the average\n"
            "5. Note any surprising entries or gaps "
            "between ranks\n\n"
            "Present as:\n"
            "- A ranked table with values and percentage of total\n"
            "- A brief insight about concentration or "
            "distribution\n"
            "- One actionable observation"
        )
