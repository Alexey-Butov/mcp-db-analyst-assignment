# tests/test_valid_queries.py
import requests

BASE_URL = "http://127.0.0.1:8000"


def run(query):
    resp = requests.post(f"{BASE_URL}/run_sql_query", json={"query": query})
    resp.raise_for_status()
    return resp.json()


def test_select_all_products():
    result = run("SELECT * FROM products LIMIT 5")
    assert "columns" in result
    assert "rows" in result
    assert len(result["rows"]) <= 5
    assert len(result["columns"]) == 3  # id, name, price
    # Optional: check sample data exists
    assert any("Laptop" in str(row) for row in result["rows"])


def test_count_orders():
    result = run("SELECT COUNT(*) FROM orders")
    assert result["rows"][0][0] >= 0


def test_join_query():
    query = """
    SELECT p.name, o.quantity
    FROM products p
    JOIN orders o ON p.id = o.product_id
    LIMIT 5
    """
    result = run(query)
    assert len(result["rows"]) <= 5
    assert len(result["columns"]) == 2