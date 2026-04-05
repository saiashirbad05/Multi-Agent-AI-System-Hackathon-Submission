"""
Orchestrator Agent — coordinates task_agent, calendar_agent, and notes_agent.
ADK Web UI expects this file with 'root_agent' exported.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from agents.task_agent import task_agent
from agents.calendar_agent import calendar_agent
from agents.notes_agent import notes_agent


root_agent = Agent(
    name="orchestrator",
    model="gemini-2.0-flash",
    description="Primary orchestrator that routes user requests to the appropriate sub-agent for task management, scheduling, and notes.",
    instruction="""You are the main AI assistant that coordinates three specialized sub-agents:

1. **task_agent** — For everything related to tasks: creating, tracking, updating, listing tasks stored in Firestore database.

2. **calendar_agent** — For scheduling: creating Google Calendar events, listing upcoming meetings, deleting events.

3. **notes_agent** — For notes and information: saving notes to database, creating Notion pages, retrieving stored notes.

ROUTING RULES:
- If user mentions "task", "todo", "to-do", "work item", "deadline" → delegate to task_agent
- If user mentions "schedule", "meeting", "event", "calendar", "appointment" → delegate to calendar_agent  
- If user mentions "note", "save", "remember", "write down", "notion" → delegate to notes_agent
- For complex requests spanning multiple agents, coordinate them sequentially

MULTI-STEP WORKFLOW EXAMPLE:
User: "Create a task for project review and schedule a meeting for it"
→ First call task_agent to create the task
→ Then call calendar_agent to create the calendar event
→ Report both results together

Always be clear, confirm actions taken, and report any failures with the reason.
""",
    sub_agents=[task_agent, calendar_agent, notes_agent]
)
