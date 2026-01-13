# agent/agent.py
"""
Thin entry point for the MCP Database Analyst Agent.
Orchestrates the agent loop via CLI.
"""

import sys

from agent.agent_loop import run_agent


def main():
    if len(sys.argv) < 2:
        print('Usage: python -m agent.agent "שאלה בעברית או באנגלית"')
        print('   or: python agent/agent.py "מה המוצר הכי נמכר?"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    answer = run_agent(question)
    print(answer)


if __name__ == "__main__":
    main()