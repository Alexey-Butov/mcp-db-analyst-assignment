#!/usr/bin/env python3
"""
init_db.py - Initialize the sample SQLite database for the MCP DB Analyst assignment.

Creates two tables:
  - products (id, name, price)
  - orders   (id, product_id, quantity, order_date)

Populates them with realistic sample data.

Safe to re-run: drops tables only if they exist.
"""

import os
import sqlite3
from typing import List, Tuple

# ────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────

DB_PATH = os.getenv("DB_PATH", "db.sqlite3")

# Table and column names as constants (helps avoid typos)
PRODUCTS_TABLE = "products"
ORDERS_TABLE = "orders"

PRODUCT_COLUMNS = ["id", "name", "price"]
ORDER_COLUMNS = ["id", "product_id", "quantity", "order_date"]


def create_schema(conn: sqlite3.Connection) -> None:
    """Create the products and orders tables if they don't exist."""
    cur = conn.cursor()

    # Drop existing tables (safe because we recreate them)
    cur.execute(f"DROP TABLE IF EXISTS {ORDERS_TABLE}")
    cur.execute(f"DROP TABLE IF EXISTS {PRODUCTS_TABLE}")

    # Products table
    cur.execute(f"""
        CREATE TABLE {PRODUCTS_TABLE} (
            id    INTEGER PRIMARY KEY,
            name  TEXT NOT NULL,
            price REAL NOT NULL
        )
    """)

    # Orders table with foreign key
    cur.execute(f"""
        CREATE TABLE {ORDERS_TABLE} (
            id         INTEGER PRIMARY KEY,
            product_id INTEGER NOT NULL,
            quantity   INTEGER NOT NULL,
            order_date TEXT NOT NULL,   -- ISO format YYYY-MM-DD
            FOREIGN KEY (product_id) REFERENCES {PRODUCTS_TABLE}(id)
        )
    """)


def insert_sample_data(conn: sqlite3.Connection) -> None:
    """Insert sample products and orders."""
    cur = conn.cursor()

    # Sample products (electronics store style)
    products: List[Tuple[int, str, float]] = [
        (1, "Laptop", 4500.0),
        (2, "Mouse", 80.0),
        (3, "Keyboard", 150.0),
        (4, "Monitor", 900.0),
        (5, "USB Cable", 25.0),
    ]

    cur.executemany(
        f"INSERT INTO {PRODUCTS_TABLE} ({', '.join(PRODUCT_COLUMNS)}) VALUES (?, ?, ?)",
        products
    )

    # Sample orders (some in May, June, July 2024)
    orders: List[Tuple[int, int, int, str]] = [
        (1, 1, 2, "2024-05-03"),
        (2, 2, 10, "2024-05-10"),
        (3, 3, 5, "2024-05-11"),
        (4, 1, 1, "2024-06-01"),
        (5, 4, 3, "2024-06-15"),
        (6, 5, 20, "2024-05-20"),
        (7, 2, 4, "2024-07-01"),
    ]

    cur.executemany(
        f"INSERT INTO {ORDERS_TABLE} ({', '.join(ORDER_COLUMNS)}) VALUES (?, ?, ?, ?)",
        orders
    )


def verify_data(conn: sqlite3.Connection) -> None:
    """Quick sanity check after insertion."""
    cur = conn.cursor()

    cur.execute(f"SELECT COUNT(*) FROM {PRODUCTS_TABLE}")
    product_count = cur.fetchone()[0]

    cur.execute(f"SELECT COUNT(*) FROM {ORDERS_TABLE}")
    order_count = cur.fetchone()[0]

    print(f"→ Created {product_count} products and {order_count} orders")


def main() -> None:
    """Main entry point: create DB, schema, and sample data."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            print(f"Initializing database → {DB_PATH}")

            create_schema(conn)
            insert_sample_data(conn)
            conn.commit()

            verify_data(conn)
            print("Database initialized successfully!")

    except sqlite3.Error as e:
        print(f"SQLite error during initialization: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()