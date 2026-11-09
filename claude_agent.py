import os
import json
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ==========================================
# 1. DEFINE CUSTOM SKILLS (TOOLS)
# ==========================================
def get_user_order_status(order_id: str) -> str:
    """Simulates looking up an order status in a backend database."""
    print(f"\n[SYSTEM SKILL EXECUTED]: Querying database for Order ID: {order_id}...")
    
    database = {
        "ORD-9981": {"status": "Shipped", "carrier": "DHL", "eta": "Tomorrow"},
        "ORD-4422": {"status": "Processing in warehouse", "carrier": "Pending", "eta": "3 days"}
    }
    
    result = database.get(order_id, {"error": "Order not found"})
    return json.dumps(result)

# Map function names to executable Python code
available_tools = {
    "get_user_order_status": get_user_order_status
}

# Anthropic Tool Definition Schema (Note: uses 'input_schema' instead of 'parameters')
tools_definition = [
    {
        "name": "get_user_order_status",
        "description": "Fetch the shipping status and ETA of a customer order using their order ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order identifier, e.g., ORD-9981",
                }
            },
            "required": ["order_id"],
        },
    }
]

# ==========================================
# 2. BUILD THE AGENT HARNESS (CONTROL LOOP)
# ==========================================
def run_claude_agent(user_prompt: str):
    print(f"User Goal: {user_prompt}\n" + "-"*50)
    model = os.getenv("ANTHROPIC_MODEL")
    
    # Initialize working memory (Messages list)
    messages = [
        {"role": "user", "content": user_prompt}
    ]
    
    max_turns = 5
    turn = 0

    while turn < max_turns:
        turn += 1
        print(f"\n--- Turn {turn}: Sending context to Claude ---")
        
        # Call the Anthropic Messages API
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system="You are a helpful customer support agent. Use available tools when you need real data.",
            tools=tools_definition,
            messages=messages
        )
        
        # Check why Claude stopped generating
        print(f"[Claude Stop Reason]: {response.stop_reason}")

        if response.stop_reason == "tool_use":
            # Extract assistant's thought process and append to history
            messages.append({"role": "assistant", "content": response.content})
            
            tool_results = []
            
            # Look through content blocks for the tool call request
            for block in response.content:
                if block.type == "tool_use":
                    tool_use_id = block.id
                    function_name = block.name
                    function_args = block.input
                    
                    print(f"  -> Claude invoked skill: '{function_name}' with args: {function_args}")
                    
                    # Execute local Python function
                    if function_name in available_tools:
                        tool_output = available_tools[function_name](**function_args)
                    else:
                        tool_output = json.dumps({"error": f"Tool {function_name} not found"})
                    
                    print(f"  -> Skill Result: {tool_output}")

                    # Prepare the tool result object for Anthropic format
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": tool_output
                    })
            
            # Feed tool results back to Claude as a "user" role turn
            messages.append({
                "role": "user",
                "content": tool_results
            })
            
            continue
            
        else:
            print("\n[Claude Decision]: Final response generated.")
            # Extract final text block
            final_text = "".join([block.text for block in response.content if hasattr(block, "text")])
            return final_text

    return "Agent stopped: Reached max iteration limit."

# ==========================================
# 3. EXECUTE
# ==========================================
if __name__ == "__main__":
    query = "Hey, can you check the shipping status for my order ORD-9981?"
    final_output = run_claude_agent(query)
    
    print("\n" + "="*50)
    print("FINAL AGENT OUTPUT:\n", final_output)