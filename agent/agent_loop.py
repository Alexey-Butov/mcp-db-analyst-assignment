# agent/agent_loop.py
"""
Core agent reasoning loop: schema awareness → SQL generation → execution → self-correction → answer formatting.
"""

import json
from functools import lru_cache
from typing import Dict, Any

from .llm_client import LLMClient
from .mcp_client import MCPClient 
from mcp_db_analyst_assignment.common.prompts import SYSTEM_PROMPT # assumes pip install -e .

llm = LLMClient()
mcp = MCPClient()


@lru_cache(maxsize=1)
def build_schema_context() -> str:
    """Cache schema description (tables + sample columns) per session."""
    tables_resp = mcp.list_tables()
    tables = tables_resp.get("tables", [])

    if not tables:
        return "No tables found in the database."

    descriptions = []
    for table in tables:
        try:
            sample = mcp.run_sql(f"SELECT * FROM {table} LIMIT 1")
            cols = sample.get("columns", [])
            descriptions.append(f"Table {table}: columns = {', '.join(cols)}")
        except Exception as e:
            descriptions.append(f"Table {table}: failed to inspect ({str(e)})")

    return "\n".join(descriptions)


def clean_sql(raw: str) -> str:
    """Strip markdown fences and extra whitespace from LLM output."""
    return (
        raw.replace("```sql", "")
           .replace("```", "")
           .strip()
    )


def generate_initial_sql(question: str, schema: str) -> str:
    """Ask LLM to produce first SQL attempt."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Database schema:\n{schema}\n\n"
                f"User question: {question}\n\n"
                "Return ONLY valid SQLite SELECT or WITH query.\n"
                "No explanations, no markdown, no comments."
            ),
        },
    ]
    return clean_sql(llm.generate(messages))


def refine_sql_on_error(
    question: str,
    schema: str,
    previous_sql: str,
    error_msg: str,
) -> str:
    """Ask LLM to fix SQL based on previous error."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Previous SQL failed:\n{previous_sql}\n\n"
                f"SQLite error:\n{error_msg}\n\n"
                f"Schema:\n{schema}\n\n"
                f"Question: {question}\n\n"
                "Fix it. Return ONLY corrected SELECT/WITH query.\n"
                "No extra text."
            ),
        },
    ]
    return clean_sql(llm.generate(messages))


def format_final_answer(question: str, sql: str, result: Dict[str, Any]) -> str:
    """Turn raw result into natural language answer (Hebrew/English)."""
    preview = {
        "columns": result.get("columns", []),
        "rows": result.get("rows", [])[:10],
    }

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful data analyst. "
                "Summarize results clearly, concisely, in the language of the question."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Question: {question}\n\n"
                f"SQL used:\n{sql}\n\n"
                f"Result (first 10 rows):\n{json.dumps(preview, ensure_ascii=False, indent=2)}\n\n"
                "Answer structure:\n"
                "1. Restate / interpret the question\n"
                "2. Briefly explain what the SQL does\n"
                "3. Clear natural-language summary of the result\n"
                "4. Mention important assumptions if any"
            ),
        },
    ]
    return llm.generate(messages, temperature=0.3, max_tokens=600)


def run_agent(question: str, max_attempts: int = 3) -> str:
    """
    Full agent flow with self-correction.

    Returns:
        Natural language answer or error message in Hebrew
    """
    schema = build_schema_context()

    sql = generate_initial_sql(question, schema)
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            result = mcp.run_sql(sql)
            return format_final_answer(question, sql, result)

        except requests.exceptions.HTTPError as http_err:
            try:
                detail = http_err.response.json().get("detail", str(http_err))
            except Exception:
                detail = str(http_err)
        except Exception as e:
            detail = str(e)

        if detail == last_error:
            break  # same error → no point continuing

        last_error = detail
        sql = refine_sql_on_error(question, schema, sql, detail)

    # Final fallback message (in Hebrew, matching original)
    return (
        "לא הצלחתי להריץ שאילתה תקינה גם אחרי מספר ניסיונות.\n"
        f"שאלה: {question}\n"
        f"שאילתה אחרונה:\n{sql}\n"
        f"שגיאה אחרונה: {last_error or 'לא ידוע'}\n"
        "ייתכן שיש בעיה בסכמה, בשמות העמודות או בשאלה עצמה."
    )