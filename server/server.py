# server/server.py
"""
MCP-style Read-Only SQLite Database Server.

Provides secure, read-only access for AI agents with two main tools:
- GET /list_tables     → list available tables
- POST /run_sql_query  → execute SELECT / WITH queries only
- GET /health          → check server & DB connection status
"""

import os
import re
import time
from typing import Any, Dict, List, Tuple

import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

# ────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────

DB_PATH = os.getenv("DB_PATH", "db.sqlite3")
DEFAULT_RESULT_LIMIT = 500

ALLOWED_FIRST_KEYWORDS = {"SELECT", "WITH"}
FORBIDDEN_KEYWORDS = {
    "DROP", "INSERT", "UPDATE", "DELETE", "ALTER", "CREATE", "TRUNCATE",
    "REPLACE", "VACUUM", "ATTACH", "DETACH"
}  # extra defense-in-depth


# ────────────────────────────────────────────────
# Lifespan
# ────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage read-only SQLite connection lifecycle."""
    conn = sqlite3.connect(
        f"file:{DB_PATH}?mode=ro",
        uri=True,
        check_same_thread=False,  # Required for async FastAPI usage
    )
    app.state.conn = conn
    print(f"Read-only SQLite connection opened → {DB_PATH}")

    yield

    conn.close()
    print("SQLite connection closed.")


app = FastAPI(
    title="MCP Read-Only DB Gateway",
    description="Secure read-only SQLite interface for LLM agents",
    version="0.1.0",
    lifespan=lifespan,
)


# ────────────────────────────────────────────────
# Models
# ────────────────────────────────────────────────

class SQLQuery(BaseModel):
    query: str


class ErrorDetail(BaseModel):
    status: str = "unhealthy"
    error: str
    message: str


# ────────────────────────────────────────────────
# Validation Helpers
# ────────────────────────────────────────────────

def ensure_read_only(query: str) -> None:
    """Reject anything that is not a safe SELECT / WITH query."""
    if not query or not query.strip():
        raise HTTPException(400, detail={"error": "EMPTY_QUERY", "message": "Query cannot be empty"})

    # Remove comments
    cleaned = re.sub(r"--.*?$", "", query, flags=re.MULTILINE)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    cleaned = cleaned.strip()

    if not cleaned:
        raise HTTPException(400, detail={"error": "INVALID_QUERY", "message": "Query is empty after stripping comments"})

    # First keyword check
    first_word = cleaned.split(maxsplit=1)[0].upper()
    if first_word not in ALLOWED_FIRST_KEYWORDS:
        raise HTTPException(
            403,
            detail={"error": "WRITE_OPERATION_BLOCKED", "message": f"Only {', '.join(ALLOWED_FIRST_KEYWORDS)} allowed"}
        )

    # Extra safety: block dangerous keywords anywhere
    upper_cleaned = cleaned.upper()
    if any(kw in upper_cleaned for kw in FORBIDDEN_KEYWORDS):
        raise HTTPException(
            403,
            detail={"error": "FORBIDDEN_OPERATION", "message": "Dangerous operation keyword detected"}
        )


# ────────────────────────────────────────────────
# Endpoints
# ────────────────────────────────────────────────

@app.get("/list_tables")
def list_tables() -> Dict[str, List[str]]:
    """Return sorted list of user tables (excludes sqlite_*)."""
    try:
        cur = app.state.conn.cursor()
        cur.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        )
        return {"tables": [row[0] for row in cur.fetchall()]}
    except sqlite3.Error as exc:
        raise HTTPException(500, detail={"error": "DB_ERROR", "message": str(exc)})


@app.post("/run_sql_query")
def run_sql_query(payload: SQLQuery) -> Dict[str, Any]:
    """Execute read-only query and return result set."""
    query = payload.query.strip()
    ensure_read_only(query)

    # Prevent runaway queries
    if "limit" not in query.lower():
        query = query.rstrip("; \t\n\r") + f" LIMIT {DEFAULT_RESULT_LIMIT}"

    try:
        cur = app.state.conn.cursor()
        cur.execute(query)

        columns = [d[0] for d in cur.description] if cur.description else []
        rows: List[Tuple] = cur.fetchall()

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "was_limited": len(rows) == DEFAULT_RESULT_LIMIT,
        }
    except sqlite3.Error as exc:
        raise HTTPException(400, detail={"error": "SQL_ERROR", "message": str(exc)})
    except Exception as exc:
        raise HTTPException(500, detail={"error": "SERVER_ERROR", "message": str(exc)})


@app.get("/health")
def health_check() -> Dict[str, Any]:
    """
    Health/readiness check.
    Confirms DB connection is alive with a trivial query.
    """
    try:
        cur = app.state.conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()

        return {
            "status": "healthy",
            "database": "connected",
            "read_only": True,
            "db_path": DB_PATH,
            "timestamp": time.time(),
        }
    except sqlite3.Error as exc:
        raise HTTPException(
            status_code=503,
            detail=ErrorDetail(error="DB_CONNECTION_FAILED", message=str(exc)).model_dump()
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=ErrorDetail(error="SERVER_ERROR", message=str(exc)).model_dump()
        )


if __name__ == "__main__":
    import uvicorn
    print("Starting development server...")
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )