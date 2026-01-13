\# MCP Database Analyst Agent



A minimal \*\*MCP-style\*\* natural-language database querying system with two separated components:



1\. \*\*Read-only SQLite Server\*\* (FastAPI) — exposes secure tools for schema discovery and query execution  

2\. \*\*AI Agent\*\* (Groq LLM) — understands questions in English or Hebrew, generates SQL, executes it safely, self-corrects errors, and returns clear answers



\*\*Highlights\*\*:

\- Tool-based architecture (MCP-style)

\- Strict read-only enforcement (server-side + prompt)

\- Automatic schema discovery

\- Self-correction loop (up to 3 retries)

\- Bilingual support (Hebrew + English)

\- Clean modular code (src/ layout, no hacks in main logic)

\- Comprehensive test suite (23/23 passing)

\- Bonus Streamlit web UI



\## Project Structure (src layout)

mcp\_db\_analyst\_assignment/

├── src/

│   ├── agent/

│   │   ├── init.py

│   │   ├── agent\_main.py       # CLI entry point (renamed from agent.py)

│   │   ├── llm\_client.py

│   │   ├── mcp\_client.py

│   │   ├── agent\_loop.py

│   │   ├── ui.py               # Streamlit web interface

│   │   └── requirements.txt

│   ├── common/

│   │   ├── init.py

│   │   └── prompts.py

│   ├── server/

│   │   ├── server.py

│   │   ├── init\_db.py

│   │   └── requirements.txt

│   └── tests/

│       ├── test\_agent\_end\_to\_end.py

│       ├── test\_llm.py

│       ├── test\_readonly.py

│       ├── test\_valid\_queries.py

│       ├── test\_init\_db.py

│       └── test\_server.py

├── pyproject.toml

├── README.md

├── .gitignore

├── .env

└── docs/

└── ui-example.png          # UI screenshot (example)

text## Installation



\### Prerequisites

\- Python 3.9+

\- Groq API key (free at https://console.groq.com/keys)



\### Setup



```bash

\# Clone \& enter project

git clone https://github.com/Alexey-Butov/mcp-db-analyst-assignment.git

cd mcp-db-analyst-assignment



\# Create \& activate venv (recommended)

python -m venv venv

venv\\Scripts\\activate



\# Install project + dependencies

pip install -e .

pip install -r src/agent/requirements.txt

pip install -r src/server/requirements.txt

pip install -r src/tests/requirements.txt   # optional – for running tests

pip install streamlit                       # for UI

Create .env in root:

envGROQ\_API\_KEY=your\_groq\_api\_key\_here

GROQ\_MODEL=llama-3.3-70b-versatile

MCP\_SERVER\_URL=http://127.0.0.1:8000

Initialize Database

Bashpython src/server/init\_db.py

Creates src/server/db.sqlite3 with sample products \& orders tables.

Running the Components

1\. Start the Read-Only Server

Bashcd src/server

uvicorn server:app --reload

Endpoints:



GET /list\_tables

POST /run\_sql\_query

GET /health



Keep this terminal open.

2\. Run the Agent CLI

From project root:

Bashpython -m agent.agent\_main "מה המוצר הכי זול?"

or

Bashpython src/agent/agent\_main.py "כמה הכנסות היו בחודש מאי?"

3\. Run the Web UI (Bonus)

Bashstreamlit run src/agent/ui.py

Opens in browser at http://localhost:8501

Ask natural-language questions (supports Hebrew \& English).

UI Screenshot

MCP Database Analyst UI

Example: Asking "כמה הכנסות היו בחודש מאי?"

Running Tests

23 tests covering:



End-to-end agent flow (including refusal on impossible questions)

LLM connectivity \& instruction following

Read-only enforcement

Valid SQL execution

DB initialization

Server health check



Run from root (venv activated):

Bashpytest -v

Coverage report (current ~46%):

Bashpytest --cov=agent --cov=common --cov=server --cov-report=term-missing tests/

All tests pass (23/23). Focus on core logic; UI \& setup scripts untested.

Summary

Fully implements the assignment requirements:



MCP-style separation (server ↔ agent via HTTP tools)

Read-only enforcement (server-side + prompt)

Schema discovery \& SQL generation

Self-correction loop

Bilingual support

Clean code, src layout, no hacks

Comprehensive tests \& basic coverage



Ready for review.

Made with ❤️ by Alexey Butov

