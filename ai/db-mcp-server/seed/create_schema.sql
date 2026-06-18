CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    segment TEXT CHECK(segment IN ('regular', 'silver', 'gold', 'platinum')),
    created_at TEXT NOT NULL,
    total_spent REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    tax_rate REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    price REAL NOT NULL,
    cost_price REAL NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    unit TEXT DEFAULT 'pcs',
    active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    order_number TEXT UNIQUE NOT NULL,
    customer_id INTEGER REFERENCES customers(id),
    order_date TEXT NOT NULL,
    status TEXT CHECK(status IN ('completed', 'returned', 'cancelled')),
    subtotal REAL NOT NULL,
    tax_amount REAL NOT NULL,
    discount_amount REAL DEFAULT 0,
    total_amount REAL NOT NULL,
    payment_method TEXT CHECK(payment_method IN ('credit_card', 'paypal', 'bank_transfer', 'wallet'))
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    product_id INTEGER REFERENCES products(id),
    quantity REAL NOT NULL,
    unit_price REAL NOT NULL,
    discount REAL DEFAULT 0,
    total REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS daily_summary (
    date TEXT PRIMARY KEY,
    total_orders INTEGER,
    total_revenue REAL,
    total_tax REAL,
    unique_customers INTEGER,
    avg_order_value REAL,
    top_category TEXT
);
