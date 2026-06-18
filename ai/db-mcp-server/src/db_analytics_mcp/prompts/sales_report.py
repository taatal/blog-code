from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP):

    @mcp.prompt()
    async def monthly_sales_report(month: str = "current") -> str:
        """Generate a comprehensive monthly sales report.

        Args:
            month: Which month to analyze. Use 'current' for this month, or specify as YYYY-MM.
        """
        return f"""Analyze the sales data for {month}. Use the available database tools to gather data, then produce a report covering:

1. Total revenue and order count for the period
2. Comparison to the previous period (growth/decline percentage)
3. Top 5 products by revenue
4. Revenue breakdown by category
5. Payment method distribution
6. Customer segments contributing most revenue
7. Any notable daily patterns or anomalies

Format the output as a structured executive summary with key metrics at the top, followed by detailed breakdowns. Use tables where appropriate."""
