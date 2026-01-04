# tests/test_agent_end_to_end.py
from agent.agent import answer_question

def test_agent_simple_question():
    answer = answer_question("מה המוצר הכי זול?")
    assert isinstance(answer, str)
    assert len(answer) > 10
    print("Agent answer:", answer)

def test_agent_revenue_question():
    answer = answer_question("כמה הכנסות היו בחודש מאי?")
    assert isinstance(answer, str)
    assert len(answer) > 10
    print("Agent answer:", answer)
