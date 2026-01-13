import sqlite3
from pathlib import Path

def test_init_db_creates_tables():
    db_path = Path("server/db.sqlite3")
    assert db_path.exists(), "DB file not created"

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cur.fetchall()]
    assert "products" in tables
    assert "orders" in tables
    conn.close()