"""Task management sub-agent."""
import uuid
from google.adk.agents import Agent
from tools.firestore_tool import save_task, get_task, list_tasks, update_task_status


task_agent = Agent(
    name="task_agent",
    model="gemini-2.0-flash-lite",
    description="Manages user tasks — creates, retrieves, lists, and updates task status in Firestore.",
    instruction="""You are a Task Manager Agent. Your job:
- Create tasks with IDs, titles, descriptions, due dates
- Retrieve specific tasks by ID
- List all tasks or filter by status (pending/completed/in-progress)
- Update task status

Always confirm actions and provide task IDs to users.
When creating a task, generate a unique ID like 'task_<short_uuid>'.
""",
    tools=[save_task, get_task, list_tasks, update_task_status]
)
