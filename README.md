\# MCP Database Analyst Agent



A minimal \*\*MCP-style\*\* natural-language database querying system with two separated components:



1\. \*\*Read-only SQLite Server\*\* (FastAPI) – exposes secure tools for schema discovery and query execution  

2\. \*\*AI Agent\*\* (Groq LLM) – understands questions in English or Hebrew, generates SQL, executes it safely, self-corrects errors, and returns clear answers



This project demonstrates:

\- Tool-based agent architecture (MCP-style)

\- Secure read-only database access

\- Schema discovery \& SQL generation

\- Self-correction on errors

\- Bilingual support (Hebrew + English)

\- Clean separation of concerns

\- Comprehensive tests (18/18 passing)



\## 📂 Project Structure

mcp-db-analyst-assignment/

├── src/                        # (optional modern layout – code moved here)

│   ├── agent/

│   │   ├── init.py

│   │   ├── agent.py           # CLI entry point

│   │   ├── llm\_client.py      # Groq LLM wrapper

│   │   ├── mcp\_client.py      # HTTP client to server

│   │   ├── agent\_loop.py      # Core reasoning + self-correction

│   │   ├── ui.py              # Streamlit UI (bonus)

│   │   └── requirements.txt

│   ├── common/

│   │   ├── init.py

│   │   └── prompts.py         # System prompt

│   ├── server/

│   │   ├── server.py          # FastAPI read-only server

│   │   ├── init\_db.py         # Creates \& seeds db.sqlite3

│   │   └── requirements.txt

│   └── tests/

│       ├── test\_agent\_end\_to\_end.py

│       ├── test\_llm.py

│       ├── test\_readonly.py

│       └── test\_valid\_queries.py

├── pyproject.toml              # Package config \& pytest settings

├── README.md

├── .env                        # GROQ\_API\_KEY, etc.

└── .gitignore

text## ⚙️ Installation



\### Prerequisites

\- Python 3.9+

\- Groq API key (free at https://console.groq.com/keys)



\### Setup



1\. Clone the repo and navigate to root:



&nbsp;  ```bash

&nbsp;  git clone https://github.com/Alexey-Butov/mcp-db-analyst-assignment.git

&nbsp;  cd mcp-db-analyst-assignment



(Recommended) Create \& activate a virtual environment:Bashpython -m venv venv

venv\\Scripts\\activate    # Windows

\# or source venv/bin/activate  # Linux/macOS

Install the project in editable mode:Bashpip install -e .

pip install -r agent/requirements.txt

pip install -r server/requirements.txt

pip install -r tests/requirements.txt   # for testing

Create .env in root:envGROQ\_API\_KEY=your\_groq\_api\_key\_here

GROQ\_MODEL=llama-3.3-70b-versatile

MCP\_SERVER\_URL=http://127.0.0.1:8000



🗄️ Initialize the Database

Bashpython server/init\_db.py

Creates server/db.sqlite3 with tables products and orders + sample data.

🚀 Running the Components

1\. Start the Read-Only Server

Bashcd server

uvicorn server:app --reload

Endpoints:



GET /list\_tables – list tables

POST /run\_sql\_query – execute SELECT/WITH only

GET /health – server \& DB health check



2\. Run the AI Agent (CLI)

From project root:

Bashpython -m agent.agent "מה המוצר הכי נמכר במאי?"

or

Bashpython agent/agent.py "כמה הכנסות היו בחודש יוני?"

3\. Run the Streamlit UI (Bonus)

Bashstreamlit run agent/ui.py

Opens browser at http://localhost:8501 – ask questions naturally.

🧪 Running Tests

18 tests cover:



End-to-end agent flow

LLM connectivity \& instruction following

Read-only enforcement

Valid SQL execution



Run from root (venv activated):

Bashpytest -v

Expected: 18 passed

🔁 Self-Correction Mechanism

If LLM-generated SQL fails:



Error message is sent back to Groq

LLM attempts correction

Up to 3 retries

Fallback message in Hebrew if all fail



🛠 Technologies



Backend: FastAPI, SQLite (read-only), Uvicorn

AI: Groq (Llama-3.3-70b), python-dotenv, requests

UI: Streamlit (optional)

Testing: pytest

Packaging: pyproject.toml + setuptools (pip install -e .)



🎯 Summary

This project fully implements the assignment requirements:



MCP-style separation (server ↔ agent via HTTP tools)

Read-only enforcement (server-side, not just prompt)

Schema discovery \& SQL generation

Self-correction loop

Bilingual support

Clean code, modular structure, comprehensive tests



Ready for review. Feedback welcome!

Made with ❤️ by Alexey Butov

