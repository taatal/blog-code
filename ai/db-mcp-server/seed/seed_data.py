import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

SEED = 42
random.seed(SEED)

DB_PATH = Path(__file__).parent / "sample.db"
SCHEMA_PATH = Path(__file__).parent / "create_schema.sql"

FIRST_NAMES = [
    "James", "Emma", "Liam", "Olivia", "Noah", "Ava", "William", "Sophia",
    "Oliver", "Isabella", "Lucas", "Mia", "Henry", "Charlotte", "Alexander",
    "Amelia", "Benjamin", "Harper", "Daniel", "Evelyn", "Matthew", "Aria",
    "Samuel", "Luna", "David", "Chloe", "Joseph", "Penelope", "Carter",
    "Layla", "Owen", "Riley", "Jack", "Zoey", "Gabriel", "Nora", "Michael",
    "Lily", "Ethan", "Eleanor", "Sebastian", "Hannah", "Leo", "Lillian",
    "Adrian", "Addison", "Nathan", "Aubrey", "Ryan", "Stella",
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Anderson", "Taylor", "Thomas",
    "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
    "Clark", "Lewis", "Robinson", "Walker", "Hall", "Young", "Allen",
    "King", "Wright", "Scott", "Green", "Baker", "Adams", "Nelson",
    "Hill", "Campbell", "Mitchell", "Roberts", "Carter", "Phillips",
]

CITIES = [
    ("New York", "US"), ("Los Angeles", "US"), ("Chicago", "US"),
    ("London", "UK"), ("Manchester", "UK"), ("Birmingham", "UK"),
    ("Toronto", "CA"), ("Vancouver", "CA"), ("Montreal", "CA"),
    ("Berlin", "DE"), ("Munich", "DE"), ("Hamburg", "DE"),
    ("Paris", "FR"), ("Lyon", "FR"), ("Sydney", "AU"),
    ("Melbourne", "AU"), ("Stockholm", "SE"), ("Amsterdam", "NL"),
    ("Dublin", "IE"), ("Singapore", "SG"),
]

CATEGORIES = [
    ("Electronics", "Phones, laptops, accessories, and gadgets", 15.0),
    ("Fashion", "Clothing, shoes, and accessories", 10.0),
    ("Home & Kitchen", "Furniture, appliances, and decor", 12.0),
    ("Sports & Outdoors", "Fitness equipment, outdoor gear, and sportswear", 10.0),
    ("Books & Media", "Books, ebooks, music, and movies", 5.0),
    ("Health & Beauty", "Skincare, supplements, and personal care", 8.0),
    ("Grocery", "Food, beverages, and household essentials", 5.0),
    ("Toys & Games", "Children's toys, board games, and puzzles", 12.0),
    ("Office Supplies", "Stationery, printers, and desk accessories", 10.0),
    ("Garden & DIY", "Tools, plants, and outdoor furniture", 12.0),
]

PRODUCTS_BY_CATEGORY = {
    "Electronics": [
        ("Wireless Bluetooth Headphones", 79.99, 35.00),
        ("USB-C Fast Charger 65W", 34.99, 12.00),
        ("Mechanical Keyboard RGB", 129.99, 55.00),
        ("Portable SSD 1TB", 89.99, 45.00),
        ("Webcam HD 1080p", 49.99, 18.00),
        ("Smart Watch Fitness Tracker", 149.99, 60.00),
        ("Noise Cancelling Earbuds", 119.99, 42.00),
        ("Laptop Stand Adjustable", 39.99, 14.00),
        ("Wireless Mouse Ergonomic", 29.99, 10.00),
        ("Power Bank 20000mAh", 44.99, 16.00),
        ("HDMI Cable 2m", 12.99, 3.00),
        ("Phone Screen Protector", 9.99, 1.50),
        ("USB Hub 7-Port", 24.99, 8.00),
        ("Bluetooth Speaker Mini", 39.99, 15.00),
        ("Tablet Stand Foldable", 19.99, 6.00),
        ("Wireless Charging Pad", 24.99, 8.00),
        ("External DVD Drive", 29.99, 12.00),
        ("LED Desk Lamp Smart", 44.99, 18.00),
        ("Portable Monitor 15.6in", 199.99, 95.00),
        ("Gaming Mouse Pad XL", 19.99, 5.00),
    ],
    "Fashion": [
        ("Cotton T-Shirt Classic", 24.99, 8.00),
        ("Slim Fit Jeans", 49.99, 18.00),
        ("Running Shoes Lightweight", 89.99, 35.00),
        ("Wool Blend Sweater", 59.99, 22.00),
        ("Canvas Backpack", 39.99, 14.00),
        ("Leather Belt Classic", 29.99, 10.00),
        ("Polarized Sunglasses", 34.99, 9.00),
        ("Waterproof Jacket", 79.99, 30.00),
        ("Casual Sneakers", 64.99, 25.00),
        ("Silk Scarf", 44.99, 15.00),
        ("Denim Jacket", 69.99, 28.00),
        ("Linen Shirt", 39.99, 14.00),
        ("Athletic Shorts", 29.99, 10.00),
        ("Merino Wool Socks 3-Pack", 19.99, 6.00),
        ("Crossbody Bag", 34.99, 12.00),
        ("Baseball Cap", 14.99, 4.00),
        ("Fleece Hoodie", 44.99, 16.00),
        ("Dress Shoes Oxford", 99.99, 40.00),
        ("Winter Beanie", 14.99, 4.00),
        ("Yoga Leggings", 39.99, 12.00),
    ],
    "Home & Kitchen": [
        ("Stainless Steel Water Bottle", 24.99, 7.00),
        ("Non-Stick Pan Set 3pc", 59.99, 22.00),
        ("Bamboo Cutting Board", 19.99, 6.00),
        ("French Press Coffee Maker", 29.99, 10.00),
        ("Throw Blanket Fleece", 34.99, 12.00),
        ("LED String Lights", 14.99, 4.00),
        ("Ceramic Mug Set 4pc", 29.99, 9.00),
        ("Kitchen Scale Digital", 19.99, 7.00),
        ("Scented Candle Set", 24.99, 8.00),
        ("Storage Container Set", 34.99, 12.00),
        ("Cast Iron Skillet 12in", 44.99, 18.00),
        ("Knife Set 5pc Block", 79.99, 30.00),
        ("Cocktail Shaker Set", 29.99, 10.00),
        ("Silicone Baking Mat", 12.99, 3.50),
        ("Wall Clock Minimalist", 29.99, 10.00),
        ("Vacuum Flask 750ml", 29.99, 10.00),
        ("Bath Towel Set 4pc", 39.99, 14.00),
        ("Spice Rack 12-Jar", 24.99, 9.00),
        ("Plant Pot Ceramic", 19.99, 5.00),
        ("Blender Portable USB", 34.99, 12.00),
    ],
    "Sports & Outdoors": [
        ("Yoga Mat Premium", 34.99, 12.00),
        ("Resistance Bands Set", 24.99, 7.00),
        ("Jump Rope Speed", 14.99, 4.00),
        ("Foam Roller", 24.99, 8.00),
        ("Camping Headlamp LED", 19.99, 6.00),
        ("Hiking Water Filter", 29.99, 10.00),
        ("Cycling Gloves", 19.99, 6.00),
        ("Tennis Balls 3-Pack", 9.99, 3.00),
        ("Dry Bag Waterproof 20L", 24.99, 8.00),
        ("Fitness Tracker Band", 49.99, 18.00),
        ("Kettlebell 12kg", 39.99, 15.00),
        ("Swim Goggles", 14.99, 4.00),
        ("Camping Hammock", 34.99, 12.00),
        ("Compression Socks", 19.99, 6.00),
        ("Basketball Indoor/Outdoor", 29.99, 10.00),
        ("Bike Phone Mount", 14.99, 4.00),
        ("Pull-Up Bar Doorway", 29.99, 10.00),
        ("Insulated Water Bottle", 24.99, 8.00),
        ("Running Armband", 12.99, 3.50),
        ("Ab Roller Wheel", 19.99, 6.00),
    ],
    "Books & Media": [
        ("Productivity Planner", 14.99, 4.00),
        ("Coding Interview Guide", 34.99, 10.00),
        ("Sci-Fi Novel Collection", 29.99, 9.00),
        ("Business Strategy Book", 19.99, 6.00),
        ("Drawing Sketchbook A4", 12.99, 3.50),
        ("Language Learning Cards", 14.99, 4.00),
        ("Cookbook Mediterranean", 24.99, 8.00),
        ("Travel Photography Book", 29.99, 10.00),
        ("Self-Help Bestseller", 16.99, 5.00),
        ("History Audiobook Set", 39.99, 12.00),
        ("Children's Picture Book", 9.99, 3.00),
        ("Graphic Novel Anthology", 19.99, 7.00),
        ("DIY Electronics Kit Book", 24.99, 8.00),
        ("Mindfulness Journal", 14.99, 4.00),
        ("Music Theory Workbook", 19.99, 6.00),
        ("Poetry Collection", 12.99, 4.00),
        ("Finance for Beginners", 16.99, 5.00),
        ("Art Supplies Guide", 14.99, 4.00),
        ("World Atlas Large", 29.99, 10.00),
        ("Board Game Strategy", 24.99, 8.00),
    ],
    "Health & Beauty": [
        ("Vitamin D3 Supplements", 14.99, 4.00),
        ("Face Moisturizer SPF30", 24.99, 8.00),
        ("Electric Toothbrush", 49.99, 18.00),
        ("Hair Styling Comb Set", 12.99, 3.00),
        ("Protein Powder 1kg", 34.99, 14.00),
        ("Essential Oil Diffuser", 29.99, 10.00),
        ("Nail Care Kit", 14.99, 4.00),
        ("Lip Balm Organic 3-Pack", 9.99, 2.50),
        ("Beard Grooming Kit", 24.99, 8.00),
        ("Collagen Serum", 29.99, 9.00),
        ("Hand Cream Set", 19.99, 6.00),
        ("Sleep Mask Silk", 14.99, 4.00),
        ("Omega-3 Fish Oil", 19.99, 6.00),
        ("Dry Shampoo", 12.99, 4.00),
        ("Massage Gun Mini", 59.99, 22.00),
        ("Bath Bomb Set 6pc", 19.99, 6.00),
        ("Teeth Whitening Strips", 24.99, 8.00),
        ("Hair Mask Deep Repair", 14.99, 4.00),
        ("SPF50 Sunscreen", 16.99, 5.00),
        ("Reusable Makeup Pads", 9.99, 2.50),
    ],
    "Grocery": [
        ("Organic Coffee Beans 1kg", 19.99, 8.00),
        ("Green Tea Collection", 12.99, 4.00),
        ("Dark Chocolate 85% 3-Pack", 9.99, 3.50),
        ("Olive Oil Extra Virgin 1L", 14.99, 6.00),
        ("Mixed Nuts 500g", 11.99, 5.00),
        ("Protein Bars 12-Pack", 24.99, 10.00),
        ("Honey Raw Organic 500g", 12.99, 5.00),
        ("Oat Milk 6-Pack", 14.99, 6.00),
        ("Granola Clusters 750g", 8.99, 3.00),
        ("Dried Fruit Mix 400g", 9.99, 4.00),
        ("Pasta Variety Pack", 7.99, 2.50),
        ("Coconut Water 12-Pack", 19.99, 8.00),
        ("Peanut Butter Natural", 6.99, 2.50),
        ("Quinoa Organic 1kg", 9.99, 4.00),
        ("Hot Sauce Collection", 14.99, 5.00),
        ("Sparkling Water 24-Pack", 16.99, 7.00),
        ("Trail Mix Energy 500g", 8.99, 3.50),
        ("Matcha Powder 100g", 19.99, 7.00),
        ("Almond Butter 350g", 8.99, 3.50),
        ("Chia Seeds 500g", 7.99, 3.00),
    ],
    "Toys & Games": [
        ("Building Blocks 500pc", 29.99, 10.00),
        ("Board Game Classic", 24.99, 8.00),
        ("RC Car Off-Road", 39.99, 15.00),
        ("Puzzle 1000 Pieces", 14.99, 4.00),
        ("Art Set Kids 120pc", 19.99, 7.00),
        ("Card Game Family", 12.99, 4.00),
        ("Science Experiment Kit", 29.99, 10.00),
        ("Plush Toy Large", 24.99, 8.00),
        ("Magnetic Tiles 60pc", 34.99, 12.00),
        ("Strategy Board Game", 34.99, 12.00),
        ("Remote Control Drone", 49.99, 20.00),
        ("Wooden Train Set", 29.99, 10.00),
        ("Bubble Machine Auto", 14.99, 5.00),
        ("Play Dough Set 10-Color", 9.99, 3.00),
        ("Kite Delta Large", 14.99, 4.00),
        ("Chess Set Wooden", 24.99, 8.00),
        ("Nerf Blaster Set", 29.99, 10.00),
        ("Dollhouse Furniture", 19.99, 7.00),
        ("Telescope Kids", 34.99, 14.00),
        ("Action Figure Set", 19.99, 7.00),
    ],
    "Office Supplies": [
        ("Notebook Set 3-Pack", 14.99, 4.00),
        ("Gel Pen Set 12pc", 9.99, 2.50),
        ("Desk Organizer Bamboo", 29.99, 10.00),
        ("Sticky Notes Variety", 7.99, 2.00),
        ("Whiteboard Magnetic", 34.99, 12.00),
        ("Document Scanner", 149.99, 60.00),
        ("Ergonomic Wrist Rest", 14.99, 4.00),
        ("Filing Cabinet 3-Drawer", 89.99, 35.00),
        ("Label Maker", 29.99, 10.00),
        ("Paper Shredder", 59.99, 24.00),
        ("Highlighter Set 6pc", 6.99, 1.50),
        ("Binder Clips Assorted", 5.99, 1.50),
        ("Desk Calendar 2026", 9.99, 3.00),
        ("Mechanical Pencil Set", 12.99, 3.50),
        ("Presentation Clicker", 24.99, 8.00),
        ("Stapler Heavy Duty", 14.99, 5.00),
        ("Cable Management Kit", 12.99, 4.00),
        ("Monitor Light Bar", 39.99, 15.00),
        ("Paper A4 5-Ream Pack", 24.99, 10.00),
        ("Planner Weekly 2026", 12.99, 4.00),
    ],
    "Garden & DIY": [
        ("Pruning Shears", 19.99, 6.00),
        ("Garden Gloves Set", 12.99, 3.50),
        ("Solar Garden Lights 6pc", 24.99, 8.00),
        ("Drill Bit Set 20pc", 19.99, 7.00),
        ("Seed Starter Kit", 14.99, 4.00),
        ("Tool Box 16-inch", 29.99, 12.00),
        ("Plant Food Liquid 1L", 9.99, 3.00),
        ("LED Grow Light", 34.99, 14.00),
        ("Measuring Tape 5m", 7.99, 2.00),
        ("Garden Hose 30m", 34.99, 12.00),
        ("Raised Garden Bed Kit", 49.99, 20.00),
        ("Screwdriver Set 12pc", 14.99, 5.00),
        ("Composting Bin", 39.99, 15.00),
        ("Paint Roller Set", 12.99, 4.00),
        ("Bird Feeder Hanging", 19.99, 6.00),
        ("Level Tool Laser", 29.99, 10.00),
        ("Potting Soil 20L", 8.99, 3.00),
        ("Hedge Trimmer Electric", 59.99, 25.00),
        ("Watering Can 5L", 14.99, 4.00),
        ("Sandpaper Variety Pack", 7.99, 2.00),
    ],
}

PAYMENT_WEIGHTS = {
    "credit_card": 45,
    "paypal": 25,
    "bank_transfer": 15,
    "wallet": 15,
}


def create_database():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    schema_sql = SCHEMA_PATH.read_text()
    cursor.executescript(schema_sql)


    for i, (name, desc, tax) in enumerate(CATEGORIES, 1):
        cursor.execute(
            "INSERT INTO categories (id, name, description, tax_rate) VALUES (?, ?, ?, ?)",
            (i, name, desc, tax),
        )


    product_id = 1
    for cat_id, (cat_name, _, _) in enumerate(CATEGORIES, 1):
        products = PRODUCTS_BY_CATEGORY[cat_name]
        for name, price, cost in products:
            sku = f"{cat_name[:3].upper()}-{product_id:04d}"
            stock = random.randint(5, 200)
            cursor.execute(
                "INSERT INTO products (id, name, sku, category_id, price, cost_price, stock_quantity, unit, active) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, 'pcs', 1)",
                (product_id, name, sku, cat_id, price, cost, stock),
            )
            product_id += 1

    total_products = product_id - 1


    customers = []
    for i in range(1, 501):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@email.com"
        city, country = random.choice(CITIES)

        days_ago = random.randint(30, 540)
        created = date.today() - timedelta(days=days_ago)

        customers.append((i, name, email, city, country, created.isoformat()))
        cursor.execute(
            "INSERT INTO customers (id, name, email, city, country, segment, created_at, total_spent) "
            "VALUES (?, ?, ?, ?, ?, 'regular', ?, 0)",
            (i, name, email, city, country, created.isoformat()),
        )


    start_date = date.today() - timedelta(days=180)
    order_id = 1
    item_id = 1
    payment_methods = list(PAYMENT_WEIGHTS.keys())
    payment_probs = [PAYMENT_WEIGHTS[m] for m in payment_methods]

    for day_offset in range(180):
        current_date = start_date + timedelta(days=day_offset)
        day_of_week = current_date.weekday()


        base_orders = random.randint(22, 35)


        if day_of_week >= 5:
            base_orders = int(base_orders * 1.3)


        month = current_date.month
        if month == 11 and current_date.day >= 20:
            base_orders = int(base_orders * 2.2)
        elif month == 12 and current_date.day <= 24:
            base_orders = int(base_orders * 1.8)

        for _ in range(base_orders):
            customer_id = random.randint(1, 500)


            status_roll = random.random()
            if status_roll < 0.05:
                status = "cancelled"
            elif status_roll < 0.12:
                status = "returned"
            else:
                status = "completed"

            payment = random.choices(payment_methods, weights=payment_probs, k=1)[0]


            num_items = random.choices([1, 2, 3, 4, 5], weights=[30, 35, 20, 10, 5], k=1)[0]
            order_subtotal = 0.0
            items = []

            for _ in range(num_items):
                prod_id = random.randint(1, total_products)
                qty = random.choices([1, 2, 3], weights=[70, 20, 10], k=1)[0]

                cursor.execute("SELECT price, category_id FROM products WHERE id = ?", (prod_id,))
                prod_row = cursor.fetchone()
                if not prod_row:
                    continue
                unit_price = prod_row[0]

                item_discount = 0.0
                if random.random() < 0.15:
                    item_discount = round(unit_price * qty * random.uniform(0.05, 0.2), 2)

                item_total = round(unit_price * qty - item_discount, 2)
                order_subtotal += item_total

                items.append((item_id, order_id, prod_id, qty, unit_price, item_discount, item_total))
                item_id += 1

            if not items:
                continue


            cursor.execute(
                "SELECT c.tax_rate FROM products p JOIN categories c ON p.category_id = c.id WHERE p.id = ?",
                (items[0][2],),
            )
            tax_row = cursor.fetchone()
            avg_tax_rate = tax_row[0] if tax_row else 10.0
            tax_amount = round(order_subtotal * avg_tax_rate / 100, 2)

            order_discount = 0.0
            if order_subtotal > 100 and random.random() < 0.1:
                order_discount = round(order_subtotal * random.uniform(0.05, 0.15), 2)

            total_amount = round(order_subtotal + tax_amount - order_discount, 2)
            order_number = f"ORD-{current_date.strftime('%Y%m%d')}-{order_id:05d}"

            cursor.execute(
                "INSERT INTO orders (id, order_number, customer_id, order_date, status, "
                "subtotal, tax_amount, discount_amount, total_amount, payment_method) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (order_id, order_number, customer_id, current_date.isoformat(),
                 status, round(order_subtotal, 2), tax_amount, order_discount,
                 total_amount, payment),
            )

            for item in items:
                cursor.execute(
                    "INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, discount, total) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    item,
                )

            order_id += 1


    cursor.execute("""
        UPDATE customers SET total_spent = (
            SELECT COALESCE(SUM(o.total_amount), 0)
            FROM orders o WHERE o.customer_id = customers.id AND o.status = 'completed'
        )
    """)


    cursor.execute("UPDATE customers SET segment = 'platinum' WHERE total_spent >= 2000")
    cursor.execute("UPDATE customers SET segment = 'gold' WHERE total_spent >= 1000 AND total_spent < 2000")
    cursor.execute("UPDATE customers SET segment = 'silver' WHERE total_spent >= 400 AND total_spent < 1000")
    cursor.execute("UPDATE customers SET segment = 'regular' WHERE total_spent < 400")


    cursor.execute("""
        INSERT INTO daily_summary (date, total_orders, total_revenue, total_tax, unique_customers, avg_order_value, top_category)
        SELECT
            o.order_date,
            COUNT(*) as total_orders,
            ROUND(SUM(o.total_amount), 2) as total_revenue,
            ROUND(SUM(o.tax_amount), 2) as total_tax,
            COUNT(DISTINCT o.customer_id) as unique_customers,
            ROUND(AVG(o.total_amount), 2) as avg_order_value,
            (SELECT c.name FROM order_items oi
             JOIN products p ON oi.product_id = p.id
             JOIN categories c ON p.category_id = c.id
             JOIN orders o2 ON oi.order_id = o2.id
             WHERE o2.order_date = o.order_date AND o2.status = 'completed'
             GROUP BY c.id ORDER BY SUM(oi.total) DESC LIMIT 1) as top_category
        FROM orders o
        WHERE o.status = 'completed'
        GROUP BY o.order_date
    """)

    conn.commit()


    cursor.execute("SELECT COUNT(*) FROM customers")
    print(f"Customers: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM products")
    print(f"Products: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM orders")
    print(f"Orders: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM order_items")
    print(f"Order items: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM daily_summary")
    print(f"Daily summaries: {cursor.fetchone()[0]}")
    cursor.execute("SELECT ROUND(SUM(total_amount), 2) FROM orders WHERE status = 'completed'")
    print(f"Total revenue: ${cursor.fetchone()[0]:,.2f}")

    conn.close()
    print(f"\nDatabase created at: {DB_PATH}")


if __name__ == "__main__":
    create_database()
