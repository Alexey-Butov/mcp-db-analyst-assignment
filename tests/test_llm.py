# tests/test_llm.py
import os
import pytest
from groq import Groq
from dotenv import load_dotenv

# Optional: import your real prompt to make the test more representative
from mcp_db_analyst_assignment.common.prompts import SYSTEM_PROMPT

load_dotenv()

@pytest.fixture(scope="module")
def llm():
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    assert api_key, "GROQ_API_KEY is missing from .env"
    client = Groq(api_key=api_key)
    return client, model


def test_llm_connectivity(llm):
    """Test that the LLM responds at all."""
    client, model = llm
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": "Say 'connected'."}],
        max_tokens=10,
    )
    content = response.choices[0].message.content.strip().lower()
    print("LLM connectivity response:", content)
    assert "connected" in content


def test_llm_instruction_following(llm):
    """Test that the LLM follows explicit instructions."""
    client, model = llm
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "Respond ONLY with the number 42. No words."}
        ],
        max_tokens=5,
    )
    content = response.choices[0].message.content.strip()
    print("LLM instruction-following response:", content)
    assert content == "42"


def test_llm_sql_generation(llm):
    """Test that the LLM can generate SQL when asked."""
    client, model = llm
    schema = """
    Table products: columns = id, name, price
    Table orders: columns = id, product_id, quantity, order_date
    """
    question = "What is the total revenue?"
    response = client.chat.completions.create(
        model=model,
        messages=[
            # You can keep the simple version or use your real prompt:
            # {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "system", "content": "Return ONLY a valid SQLite SELECT query."},
            {
                "role": "user",
                "content": (
                    f"Schema:\n{schema}\n\n"
                    f"Question: {question}\n"
                ),
            },
        ],
        max_tokens=100,
    )
    sql = response.choices[0].message.content.strip()
    print("LLM raw SQL generation response:", sql)

    # Clean markdown fences
    if sql.startswith("```"):
        sql = sql.strip("`").strip()
        if sql.lower().startswith("sql"):
            sql = sql[3:].strip()
    print("LLM cleaned SQL:", sql)

    assert sql.lower().startswith(("select", "with"))
    assert "from" in sql.lower()


def test_llm_summarization(llm):
    """Test that the LLM can summarize structured data."""
    client, model = llm
    data = {
        "columns": ["product", "revenue"],
        "rows": [["USB Cable", 1200], ["Laptop", 3000]],
    }
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Summarize the data clearly."},
            {
                "role": "user",
                "content": f"Data:\n{data}\nSummarize it in one sentence.",
            },
        ],
        max_tokens=50,
    )
    summary = response.choices[0].message.content.strip()
    print("LLM summarization response:", summary)
    assert isinstance(summary, str)
    assert len(summary) > 5
    assert "USB" in summary or "Laptop" in summary