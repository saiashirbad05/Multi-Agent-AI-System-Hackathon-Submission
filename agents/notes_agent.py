"""Notes management sub-agent — uses both Firestore and Notion."""
import uuid
from google.adk.agents import Agent
from tools.firestore_tool import save_note, list_notes
from tools.notion_tool import create_notion_page, list_notion_pages, append_to_notion_page


notes_agent = Agent(
    name="notes_agent",
    model="gemini-2.0-flash-lite",
    description="Manages notes — saves to Firestore for local retrieval and syncs to Notion for external access.",
    instruction="""You are a Notes Agent. You handle:
- Saving notes to Firestore (fast local storage)
- Creating Notion pages for important notes (external sync)
- Listing all saved notes
- Appending content to existing Notion pages

When saving a note, always save to Firestore first, then optionally sync to Notion.
Generate note IDs like 'note_<short_uuid>'.
""",
    tools=[save_note, list_notes, create_notion_page, list_notion_pages, append_to_notion_page]
)
