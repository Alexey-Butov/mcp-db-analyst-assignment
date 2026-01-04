# agent/agent.py
import os
import sys
import json
from typing import List, Dict, Any
from functools import lru_cache

import requests
from groq import Groq
from dotenv import load_dotenv

# ------------------------------------------------------------
# Ensure project root is on sys.path (works in all run modes)
# ------------------------------------------------------------
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from common.prompts import SYSTEM_PROMPT

load_dotenv()

# ------------------------------------------------------------
# LLM Configuration
# ------------------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set in .env")

llm_client = Groq(api_key=GROQ_API_KEY)

# ------------------------------------------------------------
# MCP Server URL
# ------------------------------------------------------------
SERVER_BASE_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000")


# ------------------------------------------------------------
# LLM Wrapper
# ------------------------------------------------------------
def call_llm(messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 800) -> str:
    """Call Groq LLM safely and return text content."""
    response = llm_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content.strip()


def clean_sql(sql: str) -> str:
    """Remove markdown fences or accidental formatting."""
    return (
        sql.replace("```sql", "")
           .replace("```", "")
           .strip()
    )


# ------------------------------------------------------------
# MCP Tool Wrappers
# ------------------------------------------------------------
def mcp_list_tables() -> Dict[str, Any]:
    resp = requests.get(f"{SERVER_BASE_URL}/list_tables", timeout=10)
    resp.raise_for_status()
    return resp.json()


def mcp_run_sql(query: str) -> Dict[str, Any]:
    resp = requests.post(
        f"{SERVER_BASE_URL}/run_sql_query",
        json={"query": query},
        timeout=20
    )
    resp.raise_for_status()
    return resp.json()


# ------------------------------------------------------------
# Schema Discovery (cached)
# ------------------------------------------------------------
@lru_cache(maxsize=1)
def build_schema_context() -> str:
    """Fetch table list and sample columns once per session."""
    tables_resp = mcp_list_tables()
    tables = tables_resp.get("tables", [])

    if not tables:
        return "No tables found in the database."

    descriptions = []
    for t in tables:
        try:
            sample = mcp_run_sql(f"SELECT * FROM {t} LIMIT 1")
            cols = sample.get("columns", [])
            descriptions.append(f"Table {t}: columns = {', '.join(cols)}")
        except Exception as e:
            descriptions.append(f"Table {t}: failed to inspect schema ({e})")

    return "\n".join(descriptions)


# ------------------------------------------------------------
# SQL Generation
# ------------------------------------------------------------
def generate_sql_from_question(question: str, schema_context: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "Here is the current database schema:\n"
                f"{schema_context}\n\n"
                f"User question: {question}\n\n"
                "Return ONLY a valid SQLite SELECT or WITH query. "
                "No explanations, no comments, no markdown."
            ),
        },
    ]
    return clean_sql(call_llm(messages))


def refine_sql_on_error(question: str, schema_context: str, previous_sql: str, error_message: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                "The SQL you generated failed.\n\n"
                f"Previous SQL:\n{previous_sql}\n\n"
                f"SQLite error message:\n{error_message}\n\n"
                "Database schema:\n"
                f"{schema_context}\n\n"
                "Fix the SQL. Return ONLY a valid SQLite SELECT or WITH query. "
                "No explanations, no comments, no markdown."
            ),
        },
    ]
    return clean_sql(call_llm(messages))


# ------------------------------------------------------------
# Answer Formatting
# ------------------------------------------------------------
def format_answer(question: str, sql: str, result: Dict[str, Any]) -> str:
    columns = result.get("columns", [])
    rows = result.get("rows", [])

    data_preview = {
        "columns": columns,
        "rows": rows[:10],
    }

    messages = [
        {
            "role": "system",
            "content": (
                "You are a data summarization assistant. "
                "Explain results clearly and concisely."
            ),
        },
        {
            "role": "user",
            "content": (
                f"User question: {question}\n\n"
                f"Executed SQL:\n{sql}\n\n"
                f"Result preview (JSON):\n{json.dumps(data_preview, ensure_ascii=False)}\n\n"
                "In your answer, include:\n"
                "1) Interpretation of the question\n"
                "2) Brief SQL logic explanation\n"
                "3) Natural-language summary of the result separated for clarity and readability\n"
                "4) Any assumptions\n"
            ),
        },
    ]

    return call_llm(messages, temperature=0.3, max_tokens=600)


# ------------------------------------------------------------
# Main Agent Logic
# ------------------------------------------------------------
def answer_question(question: str) -> str:
    schema_context = build_schema_context()
    sql = generate_sql_from_question(question, schema_context)

    attempts = 0
    last_sql = sql
    last_error = None

    while attempts < 3:
        attempts += 1
        try:
            result = mcp_run_sql(last_sql)
            return format_answer(question, last_sql, result)

        except requests.exceptions.HTTPError as http_err:
            try:
                error_detail = http_err.response.json().get("detail", str(http_err))
            except Exception:
                error_detail = str(http_err)

            if error_detail == last_error:
                break

            last_error = error_detail
            last_sql = refine_sql_on_error(question, schema_context, last_sql, error_detail)

        except Exception as e:
            error_detail = str(e)

            if error_detail == last_error:
                break

            last_error = error_detail
            last_sql = refine_sql_on_error(question, schema_context, last_sql, error_detail)

    return (
        "לא הצלחתי להריץ שאילתה תקינה גם אחרי מספר ניסיונות.\n"
        f"שאלה: {question}\n"
        f"שאילתה אחרונה:\n{last_sql}\n"
        f"שגיאה אחרונה: {last_error}\n"
        "ייתכן שיש בעיה בסכמה או בשמות העמודות."
    )


# ------------------------------------------------------------
# CLI Entry Point
# ------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python agent.py \"שאלה בשפה טבעית\"")
        sys.exit(1)

    user_question = " ".join(sys.argv[1:])
    print(answer_question(user_question))
