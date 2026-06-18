from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP):

    @mcp.tool()
    async def get_data_dictionary(ctx) -> str:
        """Get the complete data dictionary for the connected database.

        Returns table names, column types, nullable flags, primary keys,
        and foreign key relationships. Auto-generated from the live schema.
        """
        db = ctx.request_context.lifespan_context["db"]
        return await db.generate_data_dictionary()
