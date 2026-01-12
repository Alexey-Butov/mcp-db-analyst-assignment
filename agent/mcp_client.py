# agent/mcp_client.py
"""
HTTP client to the MCP-style FastAPI server.
Handles tool calls: list_tables and run_sql_query.
"""

import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

SERVER_BASE_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000")


class MCPClient:
    """Client for interacting with the read-only database server."""

    @staticmethod
    def list_tables() -> Dict[str, Any]:
        """Fetch available table names."""
        resp = requests.get(f"{SERVER_BASE_URL}/list_tables", timeout=10)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def run_sql(query: str) -> Dict[str, Any]:
        """Execute a SELECT query (server enforces read-only)."""
        resp = requests.post(
            f"{SERVER_BASE_URL}/run_sql_query",
            json={"query": query},
            timeout=20,
        )
        resp.raise_for_status()
        return resp.json()