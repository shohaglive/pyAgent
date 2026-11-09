import sys
import argparse
from core import run_agent_loop
from tools import ALL_TOOLS_DEFINITION, ALL_TOOL_ROUTER
from db.migrations import run_migrations
from db.seeds import run_seeds

SYSTEM_PROMPT = """
You are an intelligent operations and logistics assistant. Your job is to help the user manage and inspect order statuses from the database.

### Database Schema & Code Meanings:
- order_id: The unique order identifier (e.g., ORD-1234).
- status: The operational stage code. Map these codes for the user:
  - 0 = Processing / Pending
  - 1 = Shipped / Dispatched
  - 2 = Delivered
- carrier: The shipping provider (e.g., DHL, FedEx).
- eta: Estimated time of arrival.
- notification_sent: 1 means the customer email has already been sent. 0 means it has not been sent yet.

### Response & Formatting Rules (STRICT):
1. **Translate Codes:** Never output raw codes like "status: 0". Always use plain English (Processing, Shipped, Delivered).
2. **NO BULLET POINTS:** Never use lists, bullet points, or markdown dashes (`-`). 
3. **Narrative Paragraph Only:** Always write your response as a single, fluent prose paragraph.
4. **Required Style Example:** 
   "The order ORD-12345 is currently processing, will be delivered by DHL in 3 days, and a notification has not been sent yet. Thank you"

### Core Objectives
1. Accurately call database tools to retrieve customer and order details.
2. Ensure data security and never guess or fabricate records.

### Conflict Resolution & Ambiguity Protocol
- When calling customer lookup tools, if a tool returns multiple matching records for the same name, do not guess or pick one arbitrarily.
- Immediately pause execution and ask the user for clarification using this style:
  "Multiple customers share the name [Name]. Could you please provide your email address or phone number so I can locate your exact record and find your order?"
- Once the user provides the identifier, invoke the corresponding lookup tool.
"""

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run the AI Agent application.")
    parser.add_argument(
        "--with-migration", 
        action="store_true", 
        help="Run database migrations on startup."
    )
    parser.add_argument(
        "--with-seed", 
        nargs="?", 
        const="all", 
        default=None,
        help="Run database seeding. Optionally specify a table name (e.g., --with-seed customers), or leave blank for 'all'."
    )
    return parser.parse_args()

def main():
    args = parse_arguments()

    # 1. Conditionally run migrations
    if args.with_migration:
        print("[BOOT]: Running database migrations...")
        run_migrations()
    
    # 2. Conditionally run seeds
    if args.with_seed is not None:
        target = args.with_seed
        print(f"[BOOT]: Running database seeding (target: {target})...")
        run_seeds(target)

    print("Type your query: \n")
    query=input()

    # --- Run 1: Should execute notification tool ---
    print("\n" + "="*50)
    print("RUN 1: Initial Prompt")
    print("="*50)
    output_1 = run_agent_loop(
        user_prompt=query,
        tools_definition=ALL_TOOLS_DEFINITION,
        available_tools=ALL_TOOL_ROUTER,
        system_prompt=SYSTEM_PROMPT
    )
    print("\nFINAL ANSWER:\n", output_1)


if __name__ == "__main__":
    main()