from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP):

    @mcp.prompt()
    async def top_n_analysis(entity: str = "products", metric: str = "revenue", n: int = 10) -> str:
        """Rank and analyze the top N entities by a metric.

        Args:
            entity: What to rank. Options: products, customers, categories.
            metric: Ranking metric. Options: revenue, orders, quantity.
            n: How many to return.
        """
        return f"""Find and analyze the top {n} {entity} by {metric}.

Use the database tools to:
1. Query the top {n} {entity} ranked by {metric}
2. Calculate each item's percentage contribution to the total
3. Identify concentration (does the top 20% account for 80% of {metric}?)
4. Compare the top performer to the average
5. Note any surprising entries or gaps between ranks

Present as:
- A ranked table with values and percentage of total
- A brief insight about concentration or distribution
- One actionable observation"""
