import asyncio
import re

import aiosqlite

from db_analytics_mcp.safety import validate_query, enforce_row_limit, SafetyConfig

TABLE_NAME_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


class Database:
    def __init__(self, db_path: str, config: SafetyConfig = SafetyConfig()):
        self.db_path = db_path
        self.config = config
        self._connection: aiosqlite.Connection | None = None
        self._table_cache: dict[str, list[dict]] | None = None

    async def connect(self):
        self._connection = await aiosqlite.connect(self.db_path)
        self._connection.row_factory = aiosqlite.Row
        await self._connection.execute("PRAGMA query_only = ON")
        await self._connection.execute("PRAGMA busy_timeout = 5000")

    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._connection is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._connection

    def validate_identifier(self, name: str) -> bool:
        return bool(TABLE_NAME_PATTERN.match(name))

    async def table_exists(self, table_name: str) -> bool:
        if not self.validate_identifier(table_name):
            return False
        cursor = await self.conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?",
            (table_name,),
        )
        return await cursor.fetchone() is not None

    async def column_exists(self, table_name: str, column_name: str) -> bool:
        if not self.validate_identifier(table_name) or not self.validate_identifier(column_name):
            return False
        columns = await self.get_table_schema(table_name)
        return any(c["name"] == column_name for c in columns)

    async def execute_safe_query(self, sql: str) -> dict:
        validation = validate_query(sql, self.config)
        if not validation.safe:
            return {"error": validation.reason, "rows": [], "columns": []}

        safe_sql = enforce_row_limit(sql, self.config.max_rows)

        try:
            cursor = await asyncio.wait_for(
                self.conn.execute(safe_sql),
                timeout=self.config.timeout_seconds,
            )
            rows = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []

            return {
                "columns": columns,
                "rows": [dict(row) for row in rows],
                "row_count": len(rows),
                "truncated": len(rows) >= self.config.max_rows,
            }

        except asyncio.TimeoutError:
            return {"error": f"Query timed out after {self.config.timeout_seconds}s", "rows": [], "columns": []}
        except aiosqlite.Error as e:
            return {"error": str(e), "rows": [], "columns": []}

    async def get_tables(self) -> list[dict]:
        cursor = await self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        tables = await cursor.fetchall()
        result = []
        for table in tables:
            count_cursor = await self.conn.execute(f"SELECT COUNT(*) as cnt FROM [{table['name']}]")
            count_row = await count_cursor.fetchone()
            result.append({"name": table["name"], "row_count": count_row["cnt"]})
        return result

    async def get_table_schema(self, table_name: str) -> list[dict]:
        if not self.validate_identifier(table_name):
            return []

        cache_key = table_name
        if self._table_cache and cache_key in self._table_cache:
            return self._table_cache[cache_key]

        cursor = await self.conn.execute(f"PRAGMA table_info([{table_name}])")
        columns = await cursor.fetchall()
        result = [
            {
                "name": col["name"],
                "type": col["type"],
                "nullable": not col["notnull"],
                "primary_key": bool(col["pk"]),
                "default": col["dflt_value"],
            }
            for col in columns
        ]

        if self._table_cache is None:
            self._table_cache = {}
        self._table_cache[cache_key] = result
        return result

    async def get_full_schema(self) -> str:
        cursor = await self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        rows = await cursor.fetchall()
        return "\n\n".join(row["sql"] for row in rows if row["sql"])

    async def get_foreign_keys(self, table_name: str) -> list[dict]:
        if not self.validate_identifier(table_name):
            return []
        cursor = await self.conn.execute(f"PRAGMA foreign_key_list([{table_name}])")
        rows = await cursor.fetchall()
        return [{"from": row["from"], "table": row["table"], "to": row["to"]} for row in rows]

    async def generate_data_dictionary(self) -> str:
        tables = await self.get_tables()
        lines = ["# Database Schema", ""]

        for table_info in tables:
            table_name = table_info["name"]
            row_count = table_info["row_count"]
            columns = await self.get_table_schema(table_name)
            fks = await self.get_foreign_keys(table_name)

            lines.append(f"## {table_name} ({row_count:,} rows)")
            lines.append("")
            lines.append("| Column | Type | Nullable | PK |")
            lines.append("|--------|------|----------|----|")

            for col in columns:
                pk_marker = "*" if col["primary_key"] else ""
                nullable = "YES" if col["nullable"] else "NO"
                lines.append(f"| {col['name']} | {col['type']} | {nullable} | {pk_marker} |")

            if fks:
                lines.append("")
                lines.append("Relationships:")
                for fk in fks:
                    lines.append(f"- {fk['from']} -> {fk['table']}.{fk['to']}")

            lines.append("")

        return "\n".join(lines)
