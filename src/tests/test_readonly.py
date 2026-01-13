# tests/test_readonly.py
import requests
import pytest

BASE_URL = "http://127.0.0.1:8000"


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM products",
        "UPDATE products SET price = 0",
        "INSERT INTO products (name, price) VALUES ('X', 10)",
        "DROP TABLE orders",
        "ALTER TABLE products ADD COLUMN test INT",
        "VACUUM",
        "PRAGMA writable_schema = 1",
        "CREATE TABLE test (id INT)",
        "ATTACH DATABASE 'hack.db' AS hacked",
    ],
)
def test_forbidden(sql):
    """Ensure the server blocks all write/DDL SQL operations."""
    resp = requests.post(f"{BASE_URL}/run_sql_query", json={"query": sql})
    assert resp.status_code in (400, 403), f"Server FAILED to block: {sql}"
    print(f"✔️ Correctly blocked: {sql}")