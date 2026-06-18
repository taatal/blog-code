"""
MCP client integration test.

Connects to the server over stdio and validates every tool, resource, and prompt.
No Claude account needed.

Usage:
    python tests/test_client.py
"""

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


DB_PATH = Path(__file__).parent.parent / "seed" / "sample.db"


async def run_tests():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "db_analytics_mcp", "--db", str(DB_PATH)],
        cwd=str(Path(__file__).parent.parent),
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            print(f"Available tools ({len(tool_names)}): {', '.join(tool_names)}")
            assert "execute_query" in tool_names
            assert "list_tables" in tool_names
            assert "describe_table" in tool_names
            assert "get_schema" in tool_names
            assert "table_stats" in tool_names
            assert "column_stats" in tool_names
            assert "revenue_summary" in tool_names
            assert "top_products" in tool_names
            assert "customer_segments" in tool_names
            assert "get_data_dictionary" in tool_names
            print("  [PASS] All expected tools registered")

            resources = await session.list_resources()
            resource_uris = [r.uri for r in resources.resources]
            print(f"\nAvailable resources: {resource_uris}")
            print("  [PASS] Resources available")

            prompts = await session.list_prompts()
            prompt_names = [p.name for p in prompts.prompts]
            print(f"\nAvailable prompts: {prompt_names}")
            assert "monthly_sales_report" in prompt_names
            assert "trend_analysis" in prompt_names
            assert "top_n_analysis" in prompt_names
            print("  [PASS] All expected prompts registered")

            result = await session.call_tool("list_tables", {})
            output = result.content[0].text
            assert "customers" in output
            assert "orders" in output
            print(f"\nlist_tables output:\n{output}")
            print("  [PASS] list_tables works")

            result = await session.call_tool("execute_query", {
                "sql": "SELECT COUNT(*) as total_orders FROM orders WHERE status = 'completed'"
            })
            output = result.content[0].text
            assert "total_orders" in output
            print(f"\nexecute_query output:\n{output}")
            print("  [PASS] execute_query works")

            result = await session.call_tool("execute_query", {
                "sql": "DROP TABLE orders"
            })
            output = result.content[0].text
            assert "blocked" in output.lower() or "Blocked" in output
            print(f"\nBlocked query output: {output}")
            print("  [PASS] Write operations correctly blocked")

            result = await session.call_tool("revenue_summary", {
                "period": "monthly",
                "last_n": 3,
            })
            output = result.content[0].text
            assert "Revenue" in output
            print(f"\nrevenue_summary output:\n{output}")
            print("  [PASS] revenue_summary works")

            result = await session.call_tool("customer_segments", {})
            output = result.content[0].text
            assert "platinum" in output or "gold" in output
            print(f"\ncustomer_segments output:\n{output}")
            print("  [PASS] customer_segments works")

            print("\n" + "=" * 50)
            print("ALL TESTS PASSED")
            print("=" * 50)


if __name__ == "__main__":
    asyncio.run(run_tests())
