# tests/test_readonly.py
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_forbidden():
    """Ensure the server blocks all write/DDL SQL operations."""
    forbidden_queries = [
        "DELETE FROM products",
        "UPDATE products SET price = 0",
        "INSERT INTO products (name, price) VALUES ('X', 10)",
        "DROP TABLE orders",
        "ALTER TABLE products ADD COLUMN test INT",
        "VACUUM",
        "PRAGMA writable_schema = 1",
        "CREATE TABLE test (id INT)",
        "ATTACH DATABASE 'hack.db' AS hacked",
    ]

    for sql in forbidden_queries:
        resp = requests.post(f"{BASE_URL}/run_sql_query", json={"query": sql})

        # The server must reject all write operations
        assert resp.status_code == 400, f"Server FAILED to block: {sql}"

        print(f"✔️ Correctly blocked: {sql}")
