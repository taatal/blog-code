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
    """Register the monthly sales report prompt with the MCP server."""

    @mcp.prompt()
    async def monthly_sales_report(month: str = "current") -> str:
        """Generate a comprehensive monthly sales report.

        Args:
            month: Which month to analyze. Use 'current' for this
                month, or specify as YYYY-MM.
        """
        return (
            f"Analyze the sales data for {month}. "
            "Use the available database tools to gather data, "
            "then produce a report covering:\n\n"
            "1. Total revenue and order count for the period\n"
            "2. Comparison to the previous period "
            "(growth/decline percentage)\n"
            "3. Top 5 products by revenue\n"
            "4. Revenue breakdown by category\n"
            "5. Payment method distribution\n"
            "6. Customer segments contributing most revenue\n"
            "7. Any notable daily patterns or anomalies\n\n"
            "Format the output as a structured executive summary "
            "with key metrics at the top, followed by detailed "
            "breakdowns. Use tables where appropriate."
        )
