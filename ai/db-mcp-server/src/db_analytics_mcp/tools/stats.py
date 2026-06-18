from mcp.server.fastmcp import FastMCP, Context

from db_analytics_mcp.formatting import format_table


def register(mcp: FastMCP):

    @mcp.tool()
    async def table_stats(table_name: str, ctx: Context) -> str:
        """Get summary statistics for a table: row count, column count, and
        basic info about numeric and text columns.

        Args:
            table_name: The name of the table to analyze.
        """
        db = ctx.request_context.lifespan_context["db"]

        if not await db.table_exists(table_name):
            return f"Table '{table_name}' not found."

        columns = await db.get_table_schema(table_name)

        count_result = await db.execute_safe_query(f"SELECT COUNT(*) as total FROM [{table_name}]")
        row_count = count_result["rows"][0]["total"] if count_result["rows"] else 0

        numeric_cols = [c for c in columns if c["type"].upper() in ("INTEGER", "REAL", "NUMERIC", "FLOAT", "DOUBLE")]
        text_cols = [c for c in columns if c["type"].upper() in ("TEXT", "VARCHAR", "CHAR")]

        lines = [
            f"Table: {table_name}",
            f"Total rows: {row_count:,}",
            f"Columns: {len(columns)} ({len(numeric_cols)} numeric, {len(text_cols)} text)",
            "",
        ]

        if numeric_cols:
            stat_rows = []
            for col in numeric_cols[:10]:
                stats_result = await db.execute_safe_query(
                    f"SELECT MIN([{col['name']}]) as min, MAX([{col['name']}]) as max, "
                    f"ROUND(AVG([{col['name']}]), 2) as avg FROM [{table_name}] "
                    f"WHERE [{col['name']}] IS NOT NULL"
                )
                if stats_result["rows"]:
                    row = stats_result["rows"][0]
                    stat_rows.append({"column": col["name"], "min": row["min"], "max": row["max"], "avg": row["avg"]})

            if stat_rows:
                lines.append("Numeric columns:")
                lines.append(format_table(["column", "min", "max", "avg"], stat_rows))

        return "\n".join(lines)

    @mcp.tool()
    async def column_stats(table_name: str, column_name: str, ctx: Context) -> str:
        """Get detailed statistics for a specific column including value distribution.

        Args:
            table_name: The table containing the column.
            column_name: The column to analyze.
        """
        db = ctx.request_context.lifespan_context["db"]

        if not await db.table_exists(table_name):
            return f"Table '{table_name}' not found."

        if not await db.column_exists(table_name, column_name):
            return f"Column '{column_name}' not found in '{table_name}'."

        stats_result = await db.execute_safe_query(
            f"SELECT COUNT(*) as total, "
            f"COUNT(DISTINCT [{column_name}]) as distinct_count, "
            f"SUM(CASE WHEN [{column_name}] IS NULL THEN 1 ELSE 0 END) as null_count "
            f"FROM [{table_name}]"
        )

        if not stats_result["rows"]:
            return f"Unable to compute statistics for '{table_name}.{column_name}'."

        info = stats_result["rows"][0]
        lines = [
            f"Column: {table_name}.{column_name}",
            f"Total values: {info['total']:,}",
            f"Distinct values: {info['distinct_count']:,}",
            f"Null values: {info['null_count']:,}",
            "",
        ]

        if info["distinct_count"] <= 20:
            dist_result = await db.execute_safe_query(
                f"SELECT [{column_name}] as value, COUNT(*) as count "
                f"FROM [{table_name}] GROUP BY [{column_name}] ORDER BY count DESC LIMIT 20"
            )
            if dist_result["rows"]:
                lines.append("Value distribution:")
                lines.append(format_table(["value", "count"], dist_result["rows"]))
        else:
            top_result = await db.execute_safe_query(
                f"SELECT [{column_name}] as value, COUNT(*) as count "
                f"FROM [{table_name}] GROUP BY [{column_name}] ORDER BY count DESC LIMIT 10"
            )
            if top_result["rows"]:
                lines.append("Top 10 most frequent values:")
                lines.append(format_table(["value", "count"], top_result["rows"]))

        return "\n".join(lines)
