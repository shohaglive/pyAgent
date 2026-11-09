import os
from dotenv import load_dotenv
import anthropic

print("1. Script started successfully!")

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"2. API Key found: {bool(api_key)}")

client = anthropic.Anthropic(api_key=api_key)

print("3. Sending test request to Claude...")
response = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=100,
    messages=[{"role": "user", "content": "Say hello!"}]
)

print("4. Response received!")
print("Claude says:", response.content[0].text)