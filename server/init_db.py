import sqlite3

conn = sqlite3.connect("db.sqlite3")
cur = conn.cursor()

# Drop tables if exist (רק בשלב יצירת DB)
cur.execute("DROP TABLE IF EXISTS orders")
cur.execute("DROP TABLE IF EXISTS products")

# Create products table
cur.execute("""
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL
)
""")

# Create orders table
cur.execute("""
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(id)
)
""")

# Insert sample products
products = [
    (1, "Laptop", 4500.0),
    (2, "Mouse", 80.0),
    (3, "Keyboard", 150.0),
    (4, "Monitor", 900.0),
    (5, "USB Cable", 25.0),
]

cur.executemany("INSERT INTO products VALUES (?, ?, ?)", products)

# Insert sample orders
orders = [
    (1, 1, 2, "2024-05-03"),
    (2, 2, 10, "2024-05-10"),
    (3, 3, 5, "2024-05-11"),
    (4, 1, 1, "2024-06-01"),
    (5, 4, 3, "2024-06-15"),
    (6, 5, 20, "2024-05-20"),
    (7, 2, 4, "2024-07-01"),
]

cur.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)

conn.commit()
conn.close()

print("db.sqlite3 created successfully!")
