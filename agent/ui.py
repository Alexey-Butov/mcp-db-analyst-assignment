# agent/ui.py
"""
Streamlit web UI for the MCP Database Analyst Agent.
Allows users to ask questions in natural language (Hebrew/English)
and see the reasoning + result in a friendly interface.
"""

import streamlit as st
import time

# Import the agent logic (after pip install -e . from root)
from mcp_db_analyst.agent.agent_loop import run_agent


# ────────────────────────────────────────────────
# Page configuration
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="MCP DB Analyst",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ────────────────────────────────────────────────
# Sidebar – Info & Settings
# ────────────────────────────────────────────────
with st.sidebar:
    st.title("Database Analyst Agent")
    st.markdown("Ask questions about **orders** and **products** in natural language.")
    
    st.markdown("---")
    st.caption("Supported languages: English & Hebrew")
    st.caption("Examples:")
    st.caption("• מה המוצר הכי נמכר במאי?")
    st.caption("• What's the total revenue in June?")
    st.caption("• אילו מוצרים לא נמכרו בכלל השנה?")
    
    st.markdown("---")
    st.info(
        "The agent:\n"
        "• Discovers schema automatically\n"
        "• Generates & validates SQL (read-only)\n"
        "• Self-corrects up to 3 times\n"
        "• Returns clear natural-language answers"
    )


# ────────────────────────────────────────────────
# Main chat interface
# ────────────────────────────────────────────────
st.header("Ask a question about the database")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Input box
question = st.chat_input("Type your question here... (e.g. מה המוצר הכי נמכר?)")


if question:
    # Add user message to history & display
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Agent thinking placeholder
    with st.chat_message("assistant"):
        with st.status("Thinking...", expanded=True) as status:
            status.update(label="Discovering schema...", state="running")
            time.sleep(0.4)  # small visual delay for better UX

            try:
                # Run the full agent
                answer = run_agent(question.strip())

                status.update(label="Final answer ready", state="complete")
                st.markdown(answer)

            except Exception as e:
                status.update(label="Error occurred", state="error")
                st.error(f"Something went wrong:\n\n{str(e)}")
                st.caption("Please try rephrasing the question or check server connection.")

    # Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": answer})


# ────────────────────────────────────────────────
# Footer / quick actions
# ────────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
with col2:
    st.caption(f"Running on Groq • {GROQ_MODEL}")