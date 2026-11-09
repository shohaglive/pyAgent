import os
import anthropic
from dotenv import load_dotenv
from .state import MessageState

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def run_agent_loop(
    user_prompt: str,
    tools_definition: list,
    available_tools: dict,
    system_prompt: str,
    max_turns: int = 5
) -> str:
    """Generic tool-calling loop. Coordinates LLM reasoning and server side-effects."""
    
    state = MessageState()
    state.add_user_message(user_prompt)
    turn = 0
    model=os.getenv("ANTHROPIC_MODEL")

    while turn < max_turns:
        turn += 1
        print(f"\n[Harness Loop] --- Turn {turn} ---")
        
        response = client.messages.create(
            model=model,
            max_tokens=1024,
            system=system_prompt,
            tools=tools_definition,
            messages=state.get_history()
        )

        # 1. Model requests tool invocation
        if response.stop_reason == "tool_use":
            state.add_assistant_message(response.content)
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_args = block.input
                    tool_id = block.id

                    print(f"  -> Model invoked tool '{tool_name}' with args: {tool_args}")

                    if tool_name in available_tools:
                        execution_result = available_tools[tool_name](**tool_args)
                    else:
                        execution_result = f"Error: Tool '{tool_name}' not found."

                    print(f"  -> Execution Output: {execution_result}")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_id,
                        "content": execution_result
                    })

            state.add_user_message(tool_results)

        # 2. Model outputs final text answer
        else:
            return "".join([b.text for b in response.content if hasattr(b, "text")])

    return "Error: Agent reached max iteration turns without completing task."