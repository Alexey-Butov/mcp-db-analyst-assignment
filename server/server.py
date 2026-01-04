# server/server.py
import sqlite3
import re
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

DB_PATH = "db.sqlite3"


class SQLQuery(BaseModel):
    query: str


# Lifespan handler replaces startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    conn = sqlite3.connect(
        f"file:{DB_PATH}?mode=ro",
        uri=True,
        check_same_thread=False
    )
    app.state.conn = conn
    print("SQLite connection opened (read-only).")

    yield  # <-- Application runs here

    # Shutdown
    conn.close()
    print("SQLite connection closed.")


app = FastAPI(
    title="MCP-style Read-Only DB Server",
    lifespan=lifespan
)


def ensure_read_only(query: str) -> None:
    """Strict read-only SQL enforcement."""
    if not query or not query.strip():
        raise HTTPException(
            status_code=400,
            detail={"error": "EMPTY_QUERY", "message": "Query cannot be empty"}
        )

    # Remove SQL comments
    cleaned = re.sub(r"--.*?$", "", query, flags=re.MULTILINE)
    cleaned = re.sub(r"/\*.*?\*/", "", cleaned, flags=re.DOTALL)
    cleaned = cleaned.strip()

    if not cleaned:
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_QUERY", "message": "Query contains no executable SQL"}
        )

    first_token = cleaned.split()[0].upper()

    if first_token not in ("SELECT", "WITH"):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "WRITE_OPERATION_BLOCKED",
                "message": "Only read-only SELECT/WITH queries are allowed"
            }
        )


@app.get("/list_tables")
def list_tables() -> Dict[str, Any]:
    try:
        cur = app.state.conn.cursor()
        cur.execute("""
            SELECT name 
            FROM sqlite_master 
            WHERE type='table'
            ORDER BY name
        """)
        tables = [row[0] for row in cur.fetchall()]
        return {"tables": tables}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "SERVER_ERROR", "message": str(e)}
        )


@app.post("/run_sql_query")
def run_sql_query(payload: SQLQuery) -> Dict[str, Any]:
    query = payload.query
    ensure_read_only(query)

    # Optional: enforce LIMIT to prevent huge result sets
    if "limit" not in query.lower():
        query = query.rstrip(";") + " LIMIT 500"

    try:
        cur = app.state.conn.cursor()
        cur.execute(query)

        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()

        return {"columns": columns, "rows": rows}

    except sqlite3.Error as e:
        raise HTTPException(
            status_code=400,
            detail={"error": "SQL_ERROR", "message": str(e)}
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "SERVER_ERROR", "message": str(e)}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)