import pytest
import pytest_asyncio
import aiosqlite
from pathlib import Path

from db_analytics_mcp.database import Database


SEED_DB = Path(__file__).parent.parent / "seed" / "sample.db"


@pytest_asyncio.fixture
async def db():
    database = Database(str(SEED_DB))
    await database.connect()
    yield database
    await database.close()


@pytest.mark.asyncio
async def test_get_tables(db):
    tables = await db.get_tables()
    table_names = [t["name"] for t in tables]
    assert "customers" in table_names
    assert "orders" in table_names
    assert "products" in table_names
    assert "order_items" in table_names
    assert "categories" in table_names
    assert "daily_summary" in table_names


@pytest.mark.asyncio
async def test_get_table_schema(db):
    columns = await db.get_table_schema("orders")
    col_names = [c["name"] for c in columns]
    assert "id" in col_names
    assert "order_number" in col_names
    assert "customer_id" in col_names
    assert "total_amount" in col_names
    assert "status" in col_names


@pytest.mark.asyncio
async def test_get_full_schema(db):
    schema = await db.get_full_schema()
    assert "CREATE TABLE" in schema
    assert "customers" in schema
    assert "orders" in schema


@pytest.mark.asyncio
async def test_execute_safe_query_select(db):
    result = await db.execute_safe_query("SELECT COUNT(*) as cnt FROM customers")
    assert "error" not in result
    assert result["rows"][0]["cnt"] == 500


@pytest.mark.asyncio
async def test_execute_safe_query_blocks_write(db):
    result = await db.execute_safe_query("DELETE FROM customers WHERE id = 1")
    assert "error" in result
    assert "DELETE" in result["error"]


@pytest.mark.asyncio
async def test_execute_safe_query_row_limit(db):
    result = await db.execute_safe_query("SELECT * FROM order_items")
    assert result["row_count"] <= 500
    assert result["truncated"] is True


@pytest.mark.asyncio
async def test_execute_safe_query_with_join(db):
    result = await db.execute_safe_query(
        "SELECT c.name, COUNT(o.id) as order_count "
        "FROM customers c JOIN orders o ON o.customer_id = c.id "
        "GROUP BY c.id ORDER BY order_count DESC LIMIT 5"
    )
    assert "error" not in result
    assert result["row_count"] == 5
    assert "name" in result["columns"]
    assert "order_count" in result["columns"]
