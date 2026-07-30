# =============================================================================
# Taatal Digital (digital.taatal.com)
# Copyright 2026 - All rights reserved under MIT License
#
# Project: DB Analytics MCP Server - Safe Database Queries for AI
# Author:  Taatal Digital Engineering
# Source:  https://github.com/taatal/blog-code/tree/main/ai/db-mcp-server
# =============================================================================
from mcp.server.fastmcp import FastMCP


SAMPLE_QUERIES = """# Sample Queries

## Revenue and Sales

### Total revenue this month
```sql
SELECT ROUND(SUM(total_amount), 2) as revenue
FROM orders
WHERE status = 'completed'
  AND order_date >= date('now', 'start of month')
```

### Daily revenue trend (last 30 days)
```sql
SELECT order_date, COUNT(*) as orders, ROUND(SUM(total_amount), 2) as revenue
FROM orders
WHERE status = 'completed'
  AND order_date >= date('now', '-30 days')
GROUP BY order_date
ORDER BY order_date
```

### Revenue by payment method
```sql
SELECT payment_method, COUNT(*) as orders, ROUND(SUM(total_amount), 2) as revenue
FROM orders
WHERE status = 'completed'
GROUP BY payment_method
ORDER BY revenue DESC
```

## Products

### Top selling products by revenue
```sql
SELECT p.name, p.sku, ROUND(SUM(oi.total), 2) as revenue, SUM(oi.quantity) as units_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN orders o ON oi.order_id = o.id
WHERE o.status = 'completed'
GROUP BY p.id
ORDER BY revenue DESC
LIMIT 10
```

### Low stock products (below 10 units)
```sql
SELECT name, sku, stock_quantity, price
FROM products
WHERE active = 1 AND stock_quantity < 10
ORDER BY stock_quantity ASC
```

### Product margin analysis
```sql
SELECT p.name, p.price, p.cost_price,
       ROUND((p.price - p.cost_price) / p.price * 100, 1) as margin_pct
FROM products p
WHERE p.active = 1
ORDER BY margin_pct DESC
LIMIT 20
```

## Customers

### Top customers by lifetime value
```sql
SELECT name, email, city, segment, ROUND(total_spent, 2) as lifetime_value
FROM customers
ORDER BY total_spent DESC
LIMIT 10
```

### Customer acquisition by month
```sql
SELECT strftime('%Y-%m', created_at) as month, COUNT(*) as new_customers
FROM customers
GROUP BY month
ORDER BY month DESC
```

### Customers at risk (no orders in 60+ days)
```sql
SELECT c.name, c.email, c.segment, MAX(o.order_date) as last_order
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.id
HAVING last_order < date('now', '-60 days')
ORDER BY last_order ASC
LIMIT 20
```

## Orders

### Return and cancellation rate
```sql
SELECT status, COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 1) as percentage
FROM orders
GROUP BY status
```

### Average order value by customer segment
```sql
SELECT c.segment, COUNT(o.id) as orders,
       ROUND(AVG(o.total_amount), 2) as avg_order_value,
       ROUND(SUM(o.total_amount), 2) as total_revenue
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'completed'
GROUP BY c.segment
ORDER BY avg_order_value DESC
```

## Categories

### Revenue by category
```sql
SELECT c.name as category, COUNT(DISTINCT o.id) as orders,
       ROUND(SUM(oi.total), 2) as revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN categories c ON p.category_id = c.id
JOIN orders o ON oi.order_id = o.id
WHERE o.status = 'completed'
GROUP BY c.id
ORDER BY revenue DESC
```
"""


def register(mcp: FastMCP) -> None:
    """Register the sample queries resource with the MCP server."""

    @mcp.resource("schema://sample-queries")
    async def sample_queries() -> str:
        """Example SQL queries for common analytics tasks on this database."""
        return SAMPLE_QUERIES
