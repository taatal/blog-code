import pytest
from db_analytics_mcp.safety import validate_query, enforce_row_limit, SafetyConfig


class TestValidateQuery:

    def test_valid_select(self):
        result = validate_query("SELECT * FROM orders")
        assert result.safe is True

    def test_valid_select_with_where(self):
        result = validate_query("SELECT name, email FROM customers WHERE segment = 'gold'")
        assert result.safe is True

    def test_valid_with_cte(self):
        result = validate_query("WITH totals AS (SELECT customer_id, SUM(total_amount) as s FROM orders GROUP BY customer_id) SELECT * FROM totals")
        assert result.safe is True

    def test_valid_explain(self):
        result = validate_query("EXPLAIN SELECT * FROM products")
        assert result.safe is True

    def test_blocks_insert(self):
        result = validate_query("INSERT INTO orders (id) VALUES (999)")
        assert result.safe is False
        assert "INSERT" in result.reason

    def test_blocks_update(self):
        result = validate_query("UPDATE customers SET segment = 'platinum' WHERE id = 1")
        assert result.safe is False
        assert "UPDATE" in result.reason

    def test_blocks_delete(self):
        result = validate_query("DELETE FROM orders WHERE id = 1")
        assert result.safe is False
        assert "DELETE" in result.reason

    def test_blocks_drop(self):
        result = validate_query("DROP TABLE orders")
        assert result.safe is False
        assert "DROP" in result.reason

    def test_blocks_alter(self):
        result = validate_query("ALTER TABLE orders ADD COLUMN notes TEXT")
        assert result.safe is False

    def test_blocks_create(self):
        result = validate_query("CREATE TABLE hack (id INTEGER)")
        assert result.safe is False

    def test_blocks_truncate(self):
        result = validate_query("TRUNCATE TABLE orders")
        assert result.safe is False

    def test_blocks_pragma(self):
        result = validate_query("PRAGMA table_info(orders)")
        assert result.safe is False

    def test_blocks_attach(self):
        result = validate_query("ATTACH DATABASE '/tmp/evil.db' AS evil")
        assert result.safe is False

    def test_blocks_system_tables(self):
        result = validate_query("SELECT * FROM sqlite_master")
        assert result.safe is False
        assert "system table" in result.reason.lower()

    def test_allows_replace_function(self):
        result = validate_query("SELECT REPLACE(name, ' ', '_') FROM customers")
        assert result.safe is True

    def test_empty_query(self):
        result = validate_query("")
        assert result.safe is False

    def test_comment_only_query(self):
        result = validate_query("-- just a comment")
        assert result.safe is False

    def test_length_limit(self):
        config = SafetyConfig(max_query_length=50)
        result = validate_query("SELECT * FROM orders WHERE " + "x" * 50, config)
        assert result.safe is False
        assert "length" in result.reason.lower()

    def test_blocks_select_into_pattern(self):
        result = validate_query("SELECT * INTO new_table FROM orders")
        assert result.safe is True  # SQLite doesn't support SELECT INTO, it will just error


class TestEnforceRowLimit:

    def test_adds_limit_when_missing(self):
        result = enforce_row_limit("SELECT * FROM orders")
        assert "LIMIT 500" in result

    def test_respects_existing_lower_limit(self):
        result = enforce_row_limit("SELECT * FROM orders LIMIT 10")
        assert "LIMIT 10" in result

    def test_caps_high_limit(self):
        result = enforce_row_limit("SELECT * FROM orders LIMIT 9999")
        assert "LIMIT 500" in result

    def test_strips_semicolon_before_limit(self):
        result = enforce_row_limit("SELECT * FROM orders;")
        assert "LIMIT 500" in result
        assert ";" not in result

    def test_custom_max_rows(self):
        result = enforce_row_limit("SELECT * FROM orders", max_rows=100)
        assert "LIMIT 100" in result
