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
    """Register the trend analysis prompt with the MCP server."""

    @mcp.prompt()
    async def trend_analysis(
        metric: str = "revenue", periods: int = 12
    ) -> str:
        """Analyze trends over time for a given metric.

        Args:
            metric: What to analyze. Options: revenue, orders,
                customers, avg_order_value.
            periods: Number of periods (weeks or months) to analyze.
        """
        return (
            f"Perform a trend analysis on {metric} over the "
            f"last {periods} periods.\n\n"
            "Use the database tools to:\n"
            f"1. Query the {metric} values grouped by week or "
            "month (choose the most appropriate grouping)\n"
            "2. Calculate period-over-period growth rates\n"
            "3. Identify the overall trend direction "
            "(growing, declining, stable)\n"
            "4. Find any outlier periods that deviate "
            "significantly from the trend\n"
            "5. If seasonal patterns exist, note them\n\n"
            "Present findings as:\n"
            "- A summary of the overall trend in one sentence\n"
            "- A table of period values with growth percentages\n"
            "- Notable observations or anomalies\n"
            "- A brief forecast or recommendation based on "
            "the pattern"
        )
