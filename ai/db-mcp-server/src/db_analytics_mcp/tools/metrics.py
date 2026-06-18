from mcp.server.fastmcp import FastMCP, Context

from db_analytics_mcp.formatting import format_table


VALID_PERIODS = {"daily", "weekly", "monthly"}
VALID_PRODUCT_METRICS = {"revenue", "quantity", "orders"}


def register(mcp: FastMCP):

    @mcp.tool()
    async def revenue_summary(period: str, last_n: int, ctx: Context) -> str:
        """Get revenue summary grouped by time period.

        Args:
            period: Grouping period. One of: daily, weekly, monthly.
            last_n: Number of periods to return (e.g., 6 for last 6 months).
        """
        if period not in VALID_PERIODS:
            return f"Invalid period: '{period}'. Must be one of: {', '.join(sorted(VALID_PERIODS))}."

        db = ctx.request_context.lifespan_context["db"]

        if not await db.table_exists("orders"):
            return "Required table 'orders' not found in this database."

        group_expressions = {
            "daily": "order_date",
            "weekly": "strftime('%Y-W%W', order_date)",
            "monthly": "strftime('%Y-%m', order_date)",
        }
        group_expr = group_expressions[period]
        last_n = min(max(1, last_n), 365)

        result = await db.execute_safe_query(
            f"SELECT {group_expr} as period, "
            f"COUNT(*) as orders, "
            f"ROUND(SUM(total_amount), 2) as revenue, "
            f"ROUND(AVG(total_amount), 2) as avg_order_value, "
            f"COUNT(DISTINCT customer_id) as unique_customers "
            f"FROM orders WHERE status = 'completed' "
            f"GROUP BY {group_expr} ORDER BY period DESC LIMIT {last_n}"
        )

        if "error" in result:
            return f"Query failed: {result['error']}"

        if not result["rows"]:
            return "No completed orders found for the specified period."

        header = f"Revenue Summary ({period}, last {last_n} periods)\n\n"
        return header + format_table(result["columns"], result["rows"])

    @mcp.tool()
    async def top_products(metric: str, limit: int, ctx: Context) -> str:
        """Get top products ranked by a metric.

        Args:
            metric: Ranking metric. One of: revenue, quantity, orders.
            limit: Number of products to return (max 50).
        """
        if metric not in VALID_PRODUCT_METRICS:
            return f"Invalid metric: '{metric}'. Must be one of: {', '.join(sorted(VALID_PRODUCT_METRICS))}."

        db = ctx.request_context.lifespan_context["db"]

        for table in ("orders", "order_items", "products", "categories"):
            if not await db.table_exists(table):
                return f"Required table '{table}' not found in this database."

        limit = min(max(1, limit), 50)

        aggregations = {
            "revenue": "ROUND(SUM(oi.total), 2)",
            "quantity": "ROUND(SUM(oi.quantity), 0)",
            "orders": "COUNT(DISTINCT oi.order_id)",
        }
        agg = aggregations[metric]

        result = await db.execute_safe_query(
            f"SELECT p.name as product, c.name as category, {agg} as {metric} "
            f"FROM order_items oi "
            f"JOIN products p ON oi.product_id = p.id "
            f"JOIN categories c ON p.category_id = c.id "
            f"JOIN orders o ON oi.order_id = o.id "
            f"WHERE o.status = 'completed' "
            f"GROUP BY p.id ORDER BY {metric} DESC LIMIT {limit}"
        )

        if "error" in result:
            return f"Query failed: {result['error']}"

        if not result["rows"]:
            return "No product data found."

        header = f"Top {limit} Products by {metric.title()}\n\n"
        return header + format_table(result["columns"], result["rows"])

    @mcp.tool()
    async def customer_segments(ctx: Context) -> str:
        """Segment customers by purchase frequency and total spending.

        Returns segments with counts and average metrics for each tier.
        """
        db = ctx.request_context.lifespan_context["db"]

        if not await db.table_exists("customers"):
            return "Required table 'customers' not found in this database."

        has_segment = await db.column_exists("customers", "segment")
        if not has_segment:
            return "Column 'segment' not found in customers table. Cannot compute segmentation."

        result = await db.execute_safe_query(
            "SELECT segment, "
            "COUNT(*) as customers, "
            "ROUND(AVG(total_spent), 2) as avg_spent, "
            "ROUND(SUM(total_spent), 2) as total_revenue, "
            "ROUND(SUM(total_spent) * 100.0 / (SELECT SUM(total_spent) FROM customers), 1) as revenue_pct "
            "FROM customers GROUP BY segment ORDER BY avg_spent DESC"
        )

        if "error" in result:
            return f"Query failed: {result['error']}"

        if not result["rows"]:
            return "No customer data found."

        return "Customer Segments\n\n" + format_table(result["columns"], result["rows"])
