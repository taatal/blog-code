# db-analytics-mcp

MCP server for database analytics. Query business databases safely from AI assistants.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

python3 seed/seed_data.py
db-mcp --db ./seed/sample.db
```

## Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "db-analytics": {
      "command": "/absolute/path/to/db-mcp-server/.venv/bin/python3",
      "args": ["-m", "db_analytics_mcp", "--db", "/absolute/path/to/db-mcp-server/seed/sample.db"],
      "env": {}
    }
  }
}
```

## Claude Code Configuration

```bash
claude mcp add db-analytics .venv/bin/python3 -- -m db_analytics_mcp --db /absolute/path/to/seed/sample.db
```

## Available Tools

| Tool | Description |
|------|-------------|
| `execute_query` | Run read-only SQL queries |
| `list_tables` | List tables with row counts |
| `describe_table` | Show column details for a table |
| `get_schema` | Full CREATE TABLE statements |
| `get_data_dictionary` | Auto-generated schema documentation |
| `table_stats` | Summary statistics for a table |
| `column_stats` | Value distribution for a column |
| `revenue_summary` | Revenue by time period |
| `top_products` | Product rankings by metric |
| `customer_segments` | Customer segmentation breakdown |

## Safety

All queries pass through a validation layer that blocks write operations, caps row limits at 500, and enforces a 10-second timeout. The SQLite connection is opened in read-only mode as a second layer of protection. Safety constraints are configurable via environment variables: `DB_MCP_MAX_ROWS`, `DB_MCP_TIMEOUT`, `DB_MCP_MAX_QUERY_LENGTH`.

## Testing

```bash
pip install -e ".[dev]"
pytest tests/ -v
python3 tests/test_client.py
```

## Blog Post

Companion blog post: [Build an MCP Server for Database Analytics](https://digital.taatal.com/blogs/build-mcp-server-database-analytics)
