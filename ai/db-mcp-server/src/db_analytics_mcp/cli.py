# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: DB Analytics MCP Server - Safe Database Queries for AI
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/db-mcp-server
# =============================================================================
import argparse
import sys
from pathlib import Path


def _print_banner() -> None:
    """Print the startup banner."""
    from db_analytics_mcp import __version__

    print(f"\n  Taatal Digital | DB Analytics MCP v{__version__}")
    print("  https://digital.taatal.com\n")


def main() -> None:
    """Parse CLI arguments and start the MCP server."""
    _print_banner()
    parser = argparse.ArgumentParser(
        prog="db-mcp",
        description="MCP server for database analytics",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("seed/sample.db"),
        help="Path to SQLite database (default: seed/sample.db)",
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="MCP transport type (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host address for HTTP transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for HTTP transport (default: 8000)",
    )

    args = parser.parse_args()

    if not args.db.exists():
        print(
            f"Error: Database not found at {args.db}",
            file=sys.stderr,
        )
        print(
            "Run 'python seed/seed_data.py' to create the sample database.",
            file=sys.stderr,
        )
        sys.exit(1)

    from db_analytics_mcp.server import create_server

    server = create_server(str(args.db.resolve()))

    if args.transport == "stdio":
        server.run(transport="stdio")
    else:
        server.run(
            transport="streamable-http",
            host=args.host,
            port=args.port,
        )
