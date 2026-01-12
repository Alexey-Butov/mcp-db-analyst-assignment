# tests/test_agent_end_to_end.py

from mcp_db_analyst_assignment.agent.agent_loop import run_agent

def test_agent_simple_question():
    answer = run_agent("מה המוצר הכי זול?")
    assert isinstance(answer, str)
    assert len(answer) > 10
    print("Agent answer:", answer)


def test_agent_revenue_question():
    answer = run_agent("כמה הכנסות היו בחודש מאי?")
    assert isinstance(answer, str)
    assert len(answer) > 10
    print("Agent answer:", answer)