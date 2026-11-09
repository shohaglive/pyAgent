Markdown
# Python Claude Agent Harness

A production-grade, lightweight Python AI agent harness built using the **Anthropic Claude SDK**. This repository demonstrates core agentic architecture patterns from scratch—including custom tool binding (skills), database execution loops (SQLite), and a controlled `Reason -> Act -> Observe` execution cycle without relying on heavy black-box frameworks.

---

## Architecture Overview

┌──────────────┐      ┌──────────────────────────┐      ┌─────────────────────┐
│              │─────>│      Agent Harness       │─────>│ Local SQLite DB /   │
│ User Prompt  │      │ (Control Loop & State)   │      │ External Tools      │
│              │<─────│ (Anthropic Claude (model-name))   │<─────│ (Python Functions)  │
└──────────────┘      └──────────────────────────┘      └─────────────────────┘


1. **User Prompt:** Submits a natural language goal.
2. **Agent Harness:** Manages conversation history (`messages`), enforces guardrails (max iteration turns), and dispatches model decisions.
3. **Tool Execution:** When Claude requests a tool call (e.g., `query_order_database`), the harness intercepts the arguments, runs the local database query, and feeds the raw output back as an observation.

---
## Running the Agent

This are the steps to run agent

1. **Prepare DB:** Add a new db and put the credentials in the '.env' file. Run the following command to migrate and seed data:
```
python3 main.py --with-migration --with-seed=all
```
2. **Run Agent:** Simply run python3 main.py. It will ask you for a query, give customer name, email, phone or directly the order number to check order status.

---

## Project Structure

```text
pyAiAgent/
├── venv/                 # Python virtual environment
├── shop.db               # Local SQLite database (auto-generated)
├── requirements.txt      # Python dependencies
├── .env                  # API keys (ignored in version control)
├── test_claude.py        # Basic connection check script
└── db_agent.py           # Full agent script with SQLite tool integration
Getting Started
1. Clone & Set Up Virtual Environment
Bash
git clone <your-repository-url>
cd pyAiAgent

python3 -m venv venv
source venv/bin/activate
2. Install Dependencies
Bash
pip install -r requirements.txt
3. Configure Environment Variables
Create a .env file in the root directory and add your Anthropic API key:

Code snippet
ANTHROPIC_API_KEY="sk-ant-your-actual-api-key-here"
Running the Agent
Execute the database-backed agent script:

Bash
python -u db_agent.py
Example Query Output:
User Input: "Can you look up order ORD-9981 and tell me who the carrier is and when it arrives?"

Claude Action: Invokes query_order_database(order_id="ORD-9981").

Database Result: {"order_id": "ORD-9981", "status": "Shipped", "carrier": "DHL", "eta": "Tomorrow"}

Final Output: A polished, human-readable confirmation answering the user's question.

Next Steps & Roadmap
[ ] Integrate ChromaDB for local vector search (RAG).

[ ] Implement Model Context Protocol (MCP) server connections.

[ ] Add memory checkpointers for session persistence.