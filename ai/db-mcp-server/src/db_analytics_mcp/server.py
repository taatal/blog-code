from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from db_analytics_mcp.config import load_safety_config
from db_analytics_mcp.database import Database


def create_server(db_path: str) -> FastMCP:

    @asynccontextmanager
    async def lifespan(server: FastMCP):
        config = load_safety_config()
        db = Database(db_path, config)
        await db.connect()
        try:
            yield {"db": db}
        finally:
            await db.close()

    mcp = FastMCP(
        "Database Analytics",
        instructions="Query and analyze business databases safely through natural language",
        lifespan=lifespan,
    )

    from db_analytics_mcp.tools.query import register as register_query
    from db_analytics_mcp.tools.schema import register as register_schema
    from db_analytics_mcp.tools.stats import register as register_stats
    from db_analytics_mcp.tools.metrics import register as register_metrics
    from db_analytics_mcp.resources.data_dictionary import register as register_data_dict
    from db_analytics_mcp.resources.sample_queries import register as register_samples
    from db_analytics_mcp.prompts.sales_report import register as register_sales_prompt
    from db_analytics_mcp.prompts.trend_analysis import register as register_trend_prompt
    from db_analytics_mcp.prompts.top_n import register as register_topn_prompt

    register_query(mcp)
    register_schema(mcp)
    register_stats(mcp)
    register_metrics(mcp)
    register_data_dict(mcp)
    register_samples(mcp)
    register_sales_prompt(mcp)
    register_trend_prompt(mcp)
    register_topn_prompt(mcp)

    return mcp
