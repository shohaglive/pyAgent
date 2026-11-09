import json

def check_calendar_availability(date: str) -> str:
    """Mock calendar lookup for testing multi-tool integration."""
    return json.dumps({
        "date": date,
        "available_slots": ["10:00 AM", "02:00 PM", "04:30 PM"]
    })

CALENDAR_TOOLS_DEFINITION = [
    {
        "name": "check_calendar_availability",
        "description": "Checks open appointment slots on a given date.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date formatted as YYYY-MM-DD"}
            },
            "required": ["date"]
        }
    }
]

CALENDAR_TOOL_ROUTER = {
    "check_calendar_availability": check_calendar_availability
}