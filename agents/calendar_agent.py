"""Calendar management sub-agent."""
from google.adk.agents import Agent
from tools.calendar_tool import create_calendar_event, list_upcoming_events, delete_calendar_event


calendar_agent = Agent(
    name="calendar_agent",
    model="gemini-2.0-flash-lite",
    description="Manages Google Calendar — creates events, lists upcoming schedules, deletes events.",
    instruction="""You are a Calendar Agent. Your responsibilities:
- Create calendar events with proper date/time format (YYYY-MM-DDTHH:MM:SS)
- List upcoming events from the user's Google Calendar
- Delete events when requested

Always confirm event creation with a link. Ask for missing details like date/time before proceeding.
Default timezone is Asia/Kolkata (IST).
""",
    tools=[create_calendar_event, list_upcoming_events, delete_calendar_event]
)
