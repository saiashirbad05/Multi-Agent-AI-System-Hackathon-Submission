import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from agents.task_agent import task_agent
from agents.calendar_agent import calendar_agent
from agents.notes_agent import notes_agent

root_agent = Agent(
    name="orchestrator",
    model="gemini-2.0-flash-lite",
    description="Primary orchestrator that coordinates task, calendar, and notes agents.",
    instruction="""You are the main AI assistant coordinating three sub-agents:

1. task_agent — handles creating, listing, updating tasks in Firestore
2. calendar_agent — handles Google Calendar events stored in Firestore
3. notes_agent — handles saving notes to Firestore and Notion

Route requests to the correct sub-agent. For multi-step requests coordinate sequentially.
All data is permanently stored in Firestore database.
""",
    sub_agents=[task_agent, calendar_agent, notes_agent]
)
