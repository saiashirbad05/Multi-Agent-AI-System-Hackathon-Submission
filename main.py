import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import uuid

app = FastAPI(title="Multi-Agent AI System", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class TaskRequest(BaseModel):
    title: str
    description: str
    due_date: str
    status: str = "pending"

class NoteRequest(BaseModel):
    title: str
    content: str
    tags: list = []

class EventRequest(BaseModel):
    title: str
    description: str
    start_time: str
    duration_minutes: int = 60

class NotionRequest(BaseModel):
    title: str
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    user_id: str = "user_001"

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "system": "Multi-Agent AI System",
        "agents": ["orchestrator", "task_agent", "calendar_agent", "notes_agent"],
        "mcp_tools": ["firestore", "notion", "google_calendar"],
        "database": "firestore"
    }

@app.get("/tasks")
async def get_tasks(status: str = None):
    from tools.firestore_tool import list_tasks
    return list_tasks(status_filter=status)

@app.post("/tasks")
async def create_task(req: TaskRequest):
    from tools.firestore_tool import save_task
    task_id = f"task_{str(uuid.uuid4())[:8]}"
    return save_task(task_id, req.title, req.description, req.due_date, req.status)

@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    from tools.firestore_tool import get_task
    return get_task(task_id)

@app.put("/tasks/{task_id}")
async def update_task(task_id: str, status: str):
    from tools.firestore_tool import update_task_status
    return update_task_status(task_id, status)

@app.get("/notes")
async def get_notes():
    from tools.firestore_tool import list_notes
    return list_notes()

@app.post("/notes")
async def create_note(req: NoteRequest):
    from tools.firestore_tool import save_note
    note_id = f"note_{str(uuid.uuid4())[:8]}"
    return save_note(note_id, req.title, req.content, req.tags)

@app.get("/events")
async def get_events():
    from tools.calendar_tool import list_upcoming_events
    return list_upcoming_events()

@app.post("/events")
async def create_event(req: EventRequest):
    from tools.calendar_tool import create_calendar_event
    return create_calendar_event(req.title, req.description, req.start_time, req.duration_minutes)

@app.get("/notion")
async def get_notion():
    from tools.notion_tool import list_notion_pages
    return list_notion_pages()

@app.post("/notion")
async def create_notion(req: NotionRequest):
    from tools.notion_tool import create_notion_page
    return create_notion_page(req.title, req.content)

@app.post("/chat")
async def chat(req: ChatRequest):
    msg = req.message.lower()
    if "task" in msg and ("list" in msg or "show" in msg or "get" in msg):
        from tools.firestore_tool import list_tasks
        data = list_tasks()
        lines = [f"- [{t['status']}] {t['title']} | due {t['due_date']}" for t in data['tasks']]
        return {"response": f"Here are your {data['count']} tasks:\n" + "\n".join(lines), "session_id": req.session_id}
    elif "note" in msg and ("list" in msg or "show" in msg or "get" in msg):
        from tools.firestore_tool import list_notes
        data = list_notes()
        lines = [f"- {n['title']}: {n['content'][:60]}" for n in data['notes']]
        return {"response": f"Here are your {data['count']} notes:\n" + "\n".join(lines), "session_id": req.session_id}
    elif "event" in msg and ("list" in msg or "show" in msg or "get" in msg):
        from tools.calendar_tool import list_upcoming_events
        data = list_upcoming_events()
        lines = [f"- {e['title']} | {e['start_time']}" for e in data['events']]
        return {"response": f"Here are your {data['count']} events:\n" + "\n".join(lines), "session_id": req.session_id}
    elif "create" in msg and "task" in msg:
        return {"response": "Use POST /tasks with title, description, due_date to create a task.", "session_id": req.session_id}
    else:
        from tools.firestore_tool import list_tasks, list_notes
        from tools.calendar_tool import list_upcoming_events
        t = list_tasks()
        n = list_notes()
        e = list_upcoming_events()
        return {"response": f"System has {t['count']} tasks, {n['count']} notes, {e['count']} events. Ask me to list tasks, notes or events.", "session_id": req.session_id}

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    from tools.firestore_tool import list_tasks, list_notes
    from tools.calendar_tool import list_upcoming_events
    from tools.notion_tool import list_notion_pages

    tasks = list_tasks()
    notes = list_notes()
    events = list_upcoming_events()
    pages = list_notion_pages()

    tasks_html = "".join([f"<tr><td>{t.get('title','')}</td><td><span class='{t.get('status','')}'>{t.get('status','')}</span></td><td>{t.get('due_date','')}</td><td>{t.get('description','')[:60]}</td></tr>" for t in tasks['tasks']])
    notes_html = "".join([f"<tr><td>{n.get('title','')}</td><td>{n.get('content','')[:80]}</td><td>{str(n.get('tags',''))}</td></tr>" for n in notes['notes']])
    events_html = "".join([f"<tr><td>{e.get('title','')}</td><td>{e.get('start_time','')}</td><td>{e.get('description','')[:60]}</td></tr>" for e in events['events']])
    pages_html = "".join([f"<tr><td>{p.get('title','')}</td><td>{p.get('id','')}</td></tr>" for p in pages['pages']])

    return f"""<!DOCTYPE html>
<html><head><title>Multi-Agent AI System</title>
<style>
body{{font-family:Arial,sans-serif;margin:0;background:#f5f5f5}}
.header{{background:#1a73e8;color:white;padding:20px 30px}}
.header h1{{margin:0;font-size:24px}}
.header p{{margin:5px 0 0;opacity:0.8}}
.content{{padding:20px 30px}}
.stats{{display:flex;gap:15px;margin-bottom:25px}}
.stat{{background:white;padding:20px;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,0.1);text-align:center;flex:1}}
.stat h3{{margin:0;color:#1a73e8;font-size:36px}}
.stat p{{margin:5px 0 0;color:#666;font-size:14px}}
.api-bar{{background:white;padding:12px 20px;border-radius:8px;margin-bottom:25px;box-shadow:0 2px 4px rgba(0,0,0,0.1)}}
code{{background:#e8f0fe;color:#1a73e8;padding:3px 8px;border-radius:4px;font-size:13px;margin:3px}}
h2{{color:#333;margin-top:25px;border-left:4px solid #1a73e8;padding-left:10px}}
table{{width:100%;border-collapse:collapse;background:white;border-radius:8px;overflow:hidden;box-shadow:0 2px 4px rgba(0,0,0,0.1);margin-bottom:25px}}
th{{background:#1a73e8;color:white;padding:12px;text-align:left;font-size:14px}}
td{{padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:14px}}
tr:hover{{background:#f8f9ff}}
.completed{{color:#137333;background:#e6f4ea;padding:3px 8px;border-radius:12px;font-size:12px}}
.pending{{color:#c5221f;background:#fce8e6;padding:3px 8px;border-radius:12px;font-size:12px}}
.in-progress{{color:#b45309;background:#fef3c7;padding:3px 8px;border-radius:12px;font-size:12px}}
</style></head>
<body>
<div class="header">
<h1>🤖 Multi-Agent AI System</h1>
<p>Google ADK | Firestore | Notion MCP | Calendar MCP | Cloud Run</p>
</div>
<div class="content">
<div class="stats">
<div class="stat"><h3>{tasks['count']}</h3><p>📋 Tasks</p></div>
<div class="stat"><h3>{notes['count']}</h3><p>📝 Notes</p></div>
<div class="stat"><h3>{events['count']}</h3><p>📅 Events</p></div>
<div class="stat"><h3>{pages['count']}</h3><p>📓 Notion Pages</p></div>
</div>
<div class="api-bar">
<strong>API:</strong>
<code>GET /tasks</code><code>POST /tasks</code>
<code>GET /notes</code><code>POST /notes</code>
<code>GET /events</code><code>POST /events</code>
<code>GET /notion</code><code>POST /notion</code>
<code>POST /chat</code><code>GET /health</code>
</div>
<h2>📋 Tasks ({tasks['count']})</h2>
<table><tr><th>Title</th><th>Status</th><th>Due Date</th><th>Description</th></tr>{tasks_html}</table>
<h2>📝 Notes ({notes['count']})</h2>
<table><tr><th>Title</th><th>Content</th><th>Tags</th></tr>{notes_html}</table>
<h2>📅 Calendar Events ({events['count']})</h2>
<table><tr><th>Title</th><th>Start Time</th><th>Description</th></tr>{events_html}</table>
<h2>📓 Notion Pages ({pages['count']})</h2>
<table><tr><th>Title</th><th>Page ID</th></tr>{pages_html}</table>
</div></body></html>"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
