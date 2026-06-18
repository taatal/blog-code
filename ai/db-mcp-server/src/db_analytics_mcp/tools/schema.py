from mcp.server.fastmcp import FastMCP, Context

from db_analytics_mcp.formatting import format_table


def register(mcp: FastMCP):

    @mcp.tool()
    async def list_tables(ctx: Context) -> str:
        """List all tables in the database with their row counts.

        Use this to understand what data is available before writing queries.
        """
        db = ctx.request_context.lifespan_context["db"]
        tables = await db.get_tables()

        if not tables:
            return "No tables found in the database."

        return format_table(
            ["name", "row_count"],
            tables,
        )

    @mcp.tool()
    async def describe_table(table_name: str, ctx: Context) -> str:
        """Show the columns, types, and constraints for a specific table.

        Args:
            table_name: The name of the table to describe.
        """
        db = ctx.request_context.lifespan_context["db"]

        if not await db.table_exists(table_name):
            return f"Table '{table_name}' not found."

        columns = await db.get_table_schema(table_name)
        fks = await db.get_foreign_keys(table_name)

        display_rows = [
            {
                "column": col["name"],
                "type": col["type"],
                "nullable": "YES" if col["nullable"] else "NO",
                "pk": "*" if col["primary_key"] else "",
                "default": col["default"] or "",
            }
            for col in columns
        ]

        output = f"Table: {table_name}\n\n"
        output += format_table(["column", "type", "nullable", "pk", "default"], display_rows)

        if fks:
            output += "\n\nRelationships:\n"
            for fk in fks:
                output += f"  {fk['from']} -> {fk['table']}.{fk['to']}\n"

        return output

    @mcp.tool()
    async def get_schema(ctx: Context) -> str:
        """Get the full database schema as CREATE TABLE statements.

        Returns the complete DDL for all tables, showing structure and relationships.
        """
        db = ctx.request_context.lifespan_context["db"]
        schema = await db.get_full_schema()
        return schema if schema else "No schema found."
