from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP):

    @mcp.prompt()
    async def trend_analysis(metric: str = "revenue", periods: int = 12) -> str:
        """Analyze trends over time for a given metric.

        Args:
            metric: What to analyze. Options: revenue, orders, customers, avg_order_value.
            periods: Number of periods (weeks or months) to analyze.
        """
        return f"""Perform a trend analysis on {metric} over the last {periods} periods.

Use the database tools to:
1. Query the {metric} values grouped by week or month (choose the most appropriate grouping)
2. Calculate period-over-period growth rates
3. Identify the overall trend direction (growing, declining, stable)
4. Find any outlier periods that deviate significantly from the trend
5. If seasonal patterns exist, note them

Present findings as:
- A summary of the overall trend in one sentence
- A table of period values with growth percentages
- Notable observations or anomalies
- A brief forecast or recommendation based on the pattern"""
