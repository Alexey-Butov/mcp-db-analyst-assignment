# tests/test_agent_end_to_end.py
import re
import pytest

from agent.agent_loop import run_agent


@pytest.mark.parametrize(
    "question, expected_substrings",
    [
        (
            "מה המוצר הכי זול?",
            ["25", "USB Cable", "זול", "הכי נמוך", "מחיר"]
        ),
        (
            "מה המוצר היקר ביותר?",
            ["4500", "Laptop", "יקר", "הכי גבוה"]
        ),
        (
            "כמה הזמנות היו בחודש מאי?",
            ["4", "מאי", "הזמנות"]
        ),
        (
            "כמה הכנסות היו בחודש מאי?",
            ["11050", "11,050", "11.050", "מאי"]
        ),
    ],
    ids=[
        "cheapest_product",
        "most_expensive_product",
        "orders_in_may",
        "revenue_in_may",
    ]
)
def test_agent_correctly_answers_sample_questions(question, expected_substrings):
    """
    End-to-end: agent should return a meaningful answer containing expected keywords/numbers.
    Uses sample data from init_db.py.
    """
    answer = run_agent(question)

    assert isinstance(answer, str), "Agent must return a string"
    assert len(answer) > 20, "Answer too short - likely error message or empty"

    normalized = answer.lower().replace(",", "").replace(" ", "").replace("₪", "").replace("שקל", "")
    found = any(sub.lower() in normalized or sub.lower() in answer.lower() for sub in expected_substrings)

    assert found, (
        f"Answer did not contain any expected substring.\n"
        f"Expected one of: {expected_substrings}\n"
        f"Actual answer: {answer}"
    )

    print(f"Question: {question}")
    print(f"Answer: {answer}\n")

def test_agent_handles_failure_gracefully():
    """
    Agent should either return fallback after failed retries or refuse impossible questions.
    """
    answer = run_agent("כמה כוכבים יש בשמיים?")

    assert isinstance(answer, str)
    assert len(answer) > 20

    refusal_patterns = [
        "לא הצלחתי", "לא ניתן", "שאלה", "נתונים", "מסד הנתונים",
        "אין", "לא קיים", "לא קשור", "חיצוני"
    ]

    assert any(pat in answer for pat in refusal_patterns), (
        f"Agent should refuse or fallback on impossible question\nActual: {answer}"
    )

    print("Refusal/fallback answer:", answer)