"""
Multi-Agent AI System — FastAPI server with beautiful production UI
"""
import os
import uuid
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Multi-Agent AI System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

BASE_URL = "https://multi-agent-system-887740208824.asia-south1.run.app"

# ─── Models ───────────────────────────────────────────────────────────────────

class TaskRequest(BaseModel):
    title: str
    description: str = ""
    due_date: str = "2026-12-31"
    status: str = "pending"

class NoteRequest(BaseModel):
    title: str
    content: str = ""
    tags: list = []

class EventRequest(BaseModel):
    title: str
    description: str = ""
    start_time: str = "2026-06-20T10:00:00"
    duration_minutes: int = 60

class NotionRequest(BaseModel):
    title: str
    content: str = ""

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    user_id: str = "user_001"

# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "system": "Multi-Agent AI System",
        "agents": ["orchestrator", "task_agent", "calendar_agent", "notes_agent"],
        "mcp_tools": ["firestore", "notion", "google_calendar"],
        "database": "firestore",
        "version": "1.0.0",
        "url": BASE_URL
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
    try:
        from tools.firestore_tool import list_tasks, list_notes, save_task, save_note
        from tools.calendar_tool import list_upcoming_events, create_calendar_event
        from tools.notion_tool import list_notion_pages, create_notion_page

        if "list" in msg and "task" in msg:
            data = list_tasks()
            lines = [f"• [{t['status']}] {t['title']} — due {t['due_date']}" for t in data['tasks']]
            return {"response": f"You have {data['count']} tasks:\n" + "\n".join(lines) if lines else "No tasks found.", "session_id": req.session_id, "agent": "task_agent"}

        elif "list" in msg and "note" in msg:
            data = list_notes()
            lines = [f"• {n['title']}: {n['content'][:60]}..." for n in data['notes']]
            return {"response": f"You have {data['count']} notes:\n" + "\n".join(lines) if lines else "No notes found.", "session_id": req.session_id, "agent": "notes_agent"}

        elif "list" in msg and "event" in msg:
            data = list_upcoming_events()
            lines = [f"• {e['title']} — {e.get('start_time', e.get('start',''))}" for e in data['events']]
            return {"response": f"You have {data['count']} events:\n" + "\n".join(lines) if lines else "No events found.", "session_id": req.session_id, "agent": "calendar_agent"}

        elif "how many" in msg and "task" in msg:
            data = list_tasks()
            completed = sum(1 for t in data['tasks'] if t['status'] == 'completed')
            pending = sum(1 for t in data['tasks'] if t['status'] == 'pending')
            return {"response": f"You have {data['count']} total tasks: {completed} completed, {pending} pending.", "session_id": req.session_id, "agent": "task_agent"}

        elif "completed" in msg and "task" in msg:
            data = list_tasks(status_filter="completed")
            lines = [f"• {t['title']}" for t in data['tasks']]
            return {"response": f"{data['count']} completed tasks:\n" + "\n".join(lines) if lines else "No completed tasks.", "session_id": req.session_id, "agent": "task_agent"}

        else:
            t = list_tasks()
            n = list_notes()
            e = list_upcoming_events()
            return {"response": f"System summary: {t['count']} tasks, {n['count']} notes, {e['count']} events. Ask me to list tasks, notes, or events — or create new ones.", "session_id": req.session_id, "agent": "orchestrator"}

    except Exception as ex:
        return {"response": f"Agent error: {str(ex)}", "session_id": req.session_id, "agent": "orchestrator"}


# ─── Dashboard UI ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Multi-Agent AI System</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0a0f;
    --bg2: #111118;
    --bg3: #16161f;
    --bg4: #1c1c28;
    --border: rgba(255,255,255,0.07);
    --border2: rgba(255,255,255,0.12);
    --text: #f0f0f5;
    --text2: #9898b0;
    --text3: #5a5a70;
    --green: #00e5a0;
    --green-dim: rgba(0,229,160,0.12);
    --green-dim2: rgba(0,229,160,0.06);
    --blue: #4f8fff;
    --blue-dim: rgba(79,143,255,0.12);
    --amber: #ffb340;
    --amber-dim: rgba(255,179,64,0.12);
    --red: #ff5566;
    --red-dim: rgba(255,85,102,0.12);
    --purple: #a78bfa;
    --purple-dim: rgba(167,139,250,0.12);
    --radius: 10px;
    --radius-lg: 14px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; overflow-x: hidden; }

  /* Ambient background */
  body::before {
    content: '';
    position: fixed; top: -200px; left: -200px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(0,229,160,0.04) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
  }
  body::after {
    content: '';
    position: fixed; bottom: -200px; right: -200px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(79,143,255,0.04) 0%, transparent 70%);
    pointer-events: none; z-index: 0;
  }

  /* Layout */
  .shell { display: flex; min-height: 100vh; position: relative; z-index: 1; }

  /* Sidebar */
  .sidebar {
    width: 220px; flex-shrink: 0;
    background: var(--bg2);
    border-right: 1px solid var(--border);
    display: flex; flex-direction: column;
    padding: 0;
    position: sticky; top: 0; height: 100vh;
    overflow-y: auto;
  }
  .sidebar-logo {
    padding: 20px 20px 16px;
    border-bottom: 1px solid var(--border);
  }
  .logo-mark {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 4px;
  }
  .logo-icon {
    width: 28px; height: 28px; border-radius: 8px;
    background: var(--green-dim);
    border: 1px solid rgba(0,229,160,0.3);
    display: flex; align-items: center; justify-content: center;
    font-size: 14px;
  }
  .logo-text { font-size: 13px; font-weight: 600; letter-spacing: -0.2px; }
  .logo-sub { font-size: 11px; color: var(--text3); font-family: 'DM Mono', monospace; }

  .nav-section { padding: 16px 12px 8px; }
  .nav-label { font-size: 10px; color: var(--text3); text-transform: uppercase; letter-spacing: 1px; padding: 0 8px; margin-bottom: 6px; font-weight: 500; }
  .nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 10px; border-radius: var(--radius);
    font-size: 13px; color: var(--text2);
    cursor: pointer; transition: all 0.15s; border: none;
    background: transparent; width: 100%; text-align: left;
    margin-bottom: 2px;
  }
  .nav-item:hover { background: var(--bg3); color: var(--text); }
  .nav-item.active { background: var(--green-dim); color: var(--green); }
  .nav-item .nav-icon { font-size: 14px; width: 18px; text-align: center; }
  .nav-count {
    margin-left: auto; font-size: 10px; font-family: 'DM Mono', monospace;
    background: var(--bg4); padding: 2px 6px; border-radius: 20px;
    color: var(--text3);
  }

  .sidebar-footer {
    margin-top: auto; padding: 16px;
    border-top: 1px solid var(--border);
  }
  .status-indicator {
    display: flex; align-items: center; gap: 8px;
    font-size: 11px; color: var(--text3);
  }
  .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); animation: pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  /* Main */
  .main { flex: 1; display: flex; flex-direction: column; min-width: 0; }

  /* Topbar */
  .topbar {
    background: var(--bg2);
    border-bottom: 1px solid var(--border);
    padding: 14px 28px;
    display: flex; align-items: center; justify-content: space-between;
    position: sticky; top: 0; z-index: 10;
  }
  .page-title { font-size: 15px; font-weight: 600; }
  .page-sub { font-size: 12px; color: var(--text3); margin-top: 1px; }
  .topbar-right { display: flex; align-items: center; gap: 10px; }
  .live-badge {
    display: flex; align-items: center; gap: 6px;
    font-size: 11px; font-family: 'DM Mono', monospace;
    background: var(--green-dim); color: var(--green);
    padding: 4px 10px; border-radius: 20px;
    border: 1px solid rgba(0,229,160,0.2);
  }
  .url-pill {
    font-size: 11px; font-family: 'DM Mono', monospace;
    color: var(--text3); background: var(--bg3);
    padding: 4px 10px; border-radius: 20px;
    border: 1px solid var(--border);
    cursor: pointer; transition: color 0.15s;
    text-decoration: none;
  }
  .url-pill:hover { color: var(--green); border-color: rgba(0,229,160,0.3); }

  /* Content */
  .content { padding: 28px; flex: 1; }

  /* Tabs */
  .tab-pane { display: none; }
  .tab-pane.active { display: block; animation: fadeIn 0.2s ease; }
  @keyframes fadeIn { from{opacity:0;transform:translateY(4px)} to{opacity:1;transform:translateY(0)} }

  /* Stats row */
  .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
  .stat-card {
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: var(--radius-lg); padding: 18px 20px;
    transition: border-color 0.2s;
  }
  .stat-card:hover { border-color: var(--border2); }
  .stat-icon { font-size: 18px; margin-bottom: 10px; }
  .stat-val { font-size: 28px; font-weight: 600; line-height: 1; margin-bottom: 4px; font-family: 'DM Mono', monospace; }
  .stat-lbl { font-size: 12px; color: var(--text3); }
  .stat-card.green .stat-val { color: var(--green); }
  .stat-card.blue .stat-val { color: var(--blue); }
  .stat-card.amber .stat-val { color: var(--amber); }
  .stat-card.purple .stat-val { color: var(--purple); }

  /* Panels */
  .panel {
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: var(--radius-lg); overflow: hidden;
    margin-bottom: 18px;
  }
  .panel-head {
    padding: 14px 20px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
  }
  .panel-title { font-size: 13px; font-weight: 600; }
  .panel-sub { font-size: 11px; color: var(--text3); margin-top: 2px; }

  /* Buttons */
  .btn {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px; font-weight: 500;
    padding: 7px 14px; border-radius: var(--radius);
    border: 1px solid var(--border2); background: transparent;
    color: var(--text2); cursor: pointer; transition: all 0.15s;
    display: inline-flex; align-items: center; gap: 6px;
  }
  .btn:hover { background: var(--bg3); color: var(--text); }
  .btn-primary {
    background: var(--green); color: var(--bg); border-color: var(--green);
    font-weight: 600;
  }
  .btn-primary:hover { background: #00cc8f; }
  .btn-sm { padding: 5px 10px; font-size: 11px; }
  .btn:disabled { opacity: 0.4; cursor: not-allowed; }

  /* Table */
  .tbl-wrap { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; }
  thead th {
    font-size: 11px; color: var(--text3); font-weight: 500;
    text-transform: uppercase; letter-spacing: 0.6px;
    padding: 10px 20px; text-align: left;
    background: var(--bg3); border-bottom: 1px solid var(--border);
  }
  tbody td {
    padding: 12px 20px; font-size: 13px;
    border-bottom: 1px solid var(--border);
    color: var(--text); vertical-align: middle;
  }
  tbody tr:last-child td { border-bottom: none; }
  tbody tr:hover td { background: var(--bg3); }
  .cell-sub { font-size: 11px; color: var(--text3); margin-top: 2px; }

  /* Badges */
  .badge { font-size: 11px; font-weight: 500; padding: 3px 9px; border-radius: 20px; display: inline-block; }
  .badge-pending { background: var(--amber-dim); color: var(--amber); }
  .badge-completed { background: var(--green-dim); color: var(--green); }
  .badge-progress { background: var(--blue-dim); color: var(--blue); }

  /* Tags */
  .tag-row { display: flex; flex-wrap: wrap; gap: 4px; }
  .tag { font-size: 11px; background: var(--bg4); color: var(--text3); padding: 2px 8px; border-radius: 20px; border: 1px solid var(--border); }

  /* Forms */
  .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; padding: 20px; }
  .form-grid.cols3 { grid-template-columns: 1fr 1fr 1fr; }
  .fg-full { grid-column: 1 / -1; }
  .form-group { display: flex; flex-direction: column; gap: 6px; }
  label { font-size: 11px; color: var(--text3); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
  input, select, textarea {
    font-family: 'DM Sans', sans-serif; font-size: 13px;
    background: var(--bg3); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 9px 12px;
    color: var(--text); outline: none; width: 100%;
    transition: border-color 0.15s;
  }
  input:focus, select:focus, textarea:focus { border-color: rgba(0,229,160,0.4); }
  select option { background: var(--bg3); }
  textarea { resize: vertical; min-height: 72px; }
  .form-actions { padding: 0 20px 20px; display: flex; align-items: center; gap: 10px; }

  /* Alert */
  .alert { font-size: 12px; padding: 9px 14px; border-radius: var(--radius); margin: 0 20px 14px; display: none; }
  .alert.show { display: block; }
  .alert-ok { background: var(--green-dim); color: var(--green); border: 1px solid rgba(0,229,160,0.2); }
  .alert-err { background: var(--red-dim); color: var(--red); border: 1px solid rgba(255,85,102,0.2); }

  /* Empty state */
  .empty-state { padding: 48px 20px; text-align: center; color: var(--text3); font-size: 13px; }
  .empty-icon { font-size: 28px; margin-bottom: 8px; }

  /* Chat */
  .chat-wrap { padding: 20px; }
  .chat-messages {
    background: var(--bg3); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 16px;
    min-height: 160px; max-height: 280px; overflow-y: auto;
    margin-bottom: 14px; display: flex; flex-direction: column; gap: 10px;
  }
  .msg { max-width: 80%; font-size: 13px; line-height: 1.55; padding: 10px 14px; border-radius: 10px; white-space: pre-line; }
  .msg-user { background: var(--green); color: var(--bg); align-self: flex-end; border-radius: 10px 10px 2px 10px; font-weight: 500; }
  .msg-agent { background: var(--bg4); color: var(--text); align-self: flex-start; border: 1px solid var(--border); border-radius: 10px 10px 10px 2px; }
  .msg-thinking { color: var(--text3); font-style: italic; }
  .chat-input-row { display: flex; gap: 10px; }
  .chat-input-row input { flex: 1; }
  .quick-prompts { display: flex; flex-wrap: wrap; gap: 6px; padding: 0 20px 20px; }
  .qp-btn { font-size: 11px; padding: 5px 12px; border-radius: 20px; border: 1px solid var(--border); background: transparent; color: var(--text3); cursor: pointer; transition: all 0.15s; font-family: 'DM Sans', sans-serif; }
  .qp-btn:hover { background: var(--bg3); color: var(--text); border-color: var(--border2); }

  /* Recent activity */
  .activity-list { padding: 4px 0; }
  .activity-item {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 10px 20px; border-bottom: 1px solid var(--border);
    transition: background 0.1s;
  }
  .activity-item:last-child { border-bottom: none; }
  .activity-item:hover { background: var(--bg3); }
  .activity-dot { width: 7px; height: 7px; border-radius: 50%; margin-top: 5px; flex-shrink: 0; }
  .activity-body { flex: 1; min-width: 0; }
  .activity-title { font-size: 13px; font-weight: 500; }
  .activity-meta { font-size: 11px; color: var(--text3); margin-top: 2px; }
  .activity-time { font-size: 11px; color: var(--text3); font-family: 'DM Mono', monospace; flex-shrink: 0; }

  /* Links */
  .links-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 16px 20px; }
  .link-card {
    background: var(--bg3); border: 1px solid var(--border);
    border-radius: var(--radius); padding: 12px 14px;
    display: flex; align-items: center; justify-content: space-between;
    text-decoration: none; transition: all 0.15s; cursor: pointer;
  }
  .link-card:hover { border-color: var(--border2); background: var(--bg4); }
  .link-card-left { display: flex; align-items: center; gap: 10px; }
  .link-icon { font-size: 16px; }
  .link-name { font-size: 13px; font-weight: 500; color: var(--text); }
  .link-url { font-size: 10px; color: var(--text3); font-family: 'DM Mono', monospace; margin-top: 1px; word-break: break-all; }
  .link-arrow { color: var(--text3); font-size: 12px; }
  .link-card:hover .link-arrow { color: var(--green); }
  .copy-toast {
    position: fixed; bottom: 24px; right: 24px;
    background: var(--green); color: var(--bg);
    font-size: 12px; font-weight: 600;
    padding: 10px 18px; border-radius: var(--radius);
    opacity: 0; transform: translateY(8px); pointer-events: none;
    transition: all 0.2s; z-index: 1000;
  }
  .copy-toast.show { opacity: 1; transform: translateY(0); }

  /* Loader */
  .loader { display: inline-block; width: 14px; height: 14px; border: 2px solid var(--border2); border-top-color: var(--green); border-radius: 50%; animation: spin 0.7s linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* Scrollbar */
  ::-webkit-scrollbar { width: 4px; height: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: var(--bg4); border-radius: 4px; }
  ::-webkit-scrollbar-thumb:hover { background: var(--text3); }

  /* Responsive */
  @media (max-width: 900px) {
    .stats-grid { grid-template-columns: repeat(2,1fr); }
    .form-grid { grid-template-columns: 1fr; }
    .links-grid { grid-template-columns: 1fr; }
  }
  @media (max-width: 700px) {
    .sidebar { display: none; }
    .content { padding: 16px; }
  }
</style>
</head>
<body>

<div class="shell">
  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="sidebar-logo">
      <div class="logo-mark">
        <div class="logo-icon">⬡</div>
        <div>
          <div class="logo-text">AgentOS</div>
        </div>
      </div>
      <div class="logo-sub">multi-agent · v1.0</div>
    </div>

    <div class="nav-section">
      <div class="nav-label">Workspace</div>
      <button class="nav-item active" onclick="showTab('dashboard',this)">
        <span class="nav-icon">◈</span> Dashboard
      </button>
      <button class="nav-item" onclick="showTab('tasks',this)">
        <span class="nav-icon">☑</span> Tasks
        <span class="nav-count" id="nav-tasks">—</span>
      </button>
      <button class="nav-item" onclick="showTab('notes',this)">
        <span class="nav-icon">◎</span> Notes
        <span class="nav-count" id="nav-notes">—</span>
      </button>
      <button class="nav-item" onclick="showTab('events',this)">
        <span class="nav-icon">◷</span> Events
        <span class="nav-count" id="nav-events">—</span>
      </button>
      <button class="nav-item" onclick="showTab('notion',this)">
        <span class="nav-icon">⬡</span> Notion
        <span class="nav-count" id="nav-notion">—</span>
      </button>
    </div>

    <div class="nav-section">
      <div class="nav-label">Agent</div>
      <button class="nav-item" onclick="showTab('chat',this)">
        <span class="nav-icon">◉</span> Chat agent
      </button>
      <button class="nav-item" onclick="showTab('links',this)">
        <span class="nav-icon">⊞</span> API links
      </button>
    </div>

    <div class="sidebar-footer">
      <div class="status-indicator">
        <div class="dot" id="status-dot" style="background:var(--text3)"></div>
        <span id="status-text">connecting...</span>
      </div>
    </div>
  </aside>

  <!-- Main -->
  <div class="main">
    <!-- Topbar -->
    <div class="topbar">
      <div>
        <div class="page-title" id="page-title">Dashboard</div>
        <div class="page-sub" id="page-sub">Overview of your multi-agent system</div>
      </div>
      <div class="topbar-right">
        <a class="url-pill" href="https://multi-agent-system-887740208824.asia-south1.run.app/docs" target="_blank">
          /docs ↗
        </a>
        <div class="live-badge">
          <div class="dot"></div>
          <span id="live-text">live</span>
        </div>
      </div>
    </div>

    <div class="content">

      <!-- DASHBOARD -->
      <div id="tab-dashboard" class="tab-pane active">
        <div class="stats-grid">
          <div class="stat-card green">
            <div class="stat-icon">☑</div>
            <div class="stat-val" id="s-tasks">—</div>
            <div class="stat-lbl">Total tasks</div>
          </div>
          <div class="stat-card blue">
            <div class="stat-icon">◎</div>
            <div class="stat-val" id="s-notes">—</div>
            <div class="stat-lbl">Notes saved</div>
          </div>
          <div class="stat-card amber">
            <div class="stat-icon">◷</div>
            <div class="stat-val" id="s-events">—</div>
            <div class="stat-lbl">Events scheduled</div>
          </div>
          <div class="stat-card purple">
            <div class="stat-icon">⬡</div>
            <div class="stat-val" id="s-notion">—</div>
            <div class="stat-lbl">Notion pages</div>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:18px;">
          <div class="panel">
            <div class="panel-head">
              <div>
                <div class="panel-title">Recent tasks</div>
                <div class="panel-sub">Latest 5 entries</div>
              </div>
              <button class="btn btn-sm" onclick="showTab('tasks',null)">View all</button>
            </div>
            <div class="tbl-wrap">
              <table>
                <thead><tr><th>Title</th><th>Status</th><th>Due</th></tr></thead>
                <tbody id="dash-tasks"></tbody>
              </table>
            </div>
          </div>
          <div class="panel">
            <div class="panel-head">
              <div>
                <div class="panel-title">Recent notes</div>
                <div class="panel-sub">Latest 5 entries</div>
              </div>
              <button class="btn btn-sm" onclick="showTab('notes',null)">View all</button>
            </div>
            <div class="tbl-wrap">
              <table>
                <thead><tr><th>Title</th><th>Tags</th></tr></thead>
                <tbody id="dash-notes"></tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="panel" style="margin-top:0">
          <div class="panel-head">
            <div class="panel-title">System info</div>
          </div>
          <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0;border-top:1px solid var(--border)">
            <div style="padding:16px 20px;border-right:1px solid var(--border)">
              <div style="font-size:11px;color:var(--text3);margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px">Platform</div>
              <div style="font-size:13px;font-weight:500">Cloud Run</div>
              <div style="font-size:11px;color:var(--text3)">asia-south1</div>
            </div>
            <div style="padding:16px 20px;border-right:1px solid var(--border)">
              <div style="font-size:11px;color:var(--text3);margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px">Database</div>
              <div style="font-size:13px;font-weight:500">Firestore</div>
              <div style="font-size:11px;color:var(--text3)">Native mode</div>
            </div>
            <div style="padding:16px 20px;border-right:1px solid var(--border)">
              <div style="font-size:11px;color:var(--text3);margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px">Agents</div>
              <div style="font-size:13px;font-weight:500" id="sys-agents">loading...</div>
            </div>
            <div style="padding:16px 20px">
              <div style="font-size:11px;color:var(--text3);margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px">MCP tools</div>
              <div style="font-size:13px;font-weight:500" id="sys-mcp">loading...</div>
            </div>
          </div>
        </div>
      </div>

      <!-- TASKS -->
      <div id="tab-tasks" class="tab-pane">
        <div class="panel">
          <div class="panel-head">
            <div class="panel-title">Create task</div>
          </div>
          <div class="form-grid">
            <div class="form-group"><label>Title *</label><input id="t-title" placeholder="Task title"></div>
            <div class="form-group"><label>Due date</label><input id="t-due" type="date"></div>
            <div class="form-group fg-full"><label>Description</label><input id="t-desc" placeholder="What needs to be done?"></div>
            <div class="form-group"><label>Status</label>
              <select id="t-status">
                <option value="pending">Pending</option>
                <option value="in-progress">In progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>
          <div id="task-alert" class="alert"></div>
          <div class="form-actions">
            <button class="btn btn-primary" id="task-submit-btn" onclick="createTask()">Create task</button>
            <span style="font-size:11px;color:var(--text3)">Saved permanently to Firestore</span>
          </div>
        </div>
        <div class="panel">
          <div class="panel-head">
            <div><div class="panel-title">All tasks</div><div class="panel-sub" id="tasks-count-lbl">Loading...</div></div>
            <button class="btn btn-sm" onclick="loadTasks()">↻ Refresh</button>
          </div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>Title</th><th>Description</th><th>Status</th><th>Due date</th><th>Created</th></tr></thead>
              <tbody id="tasks-tbody"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- NOTES -->
      <div id="tab-notes" class="tab-pane">
        <div class="panel">
          <div class="panel-head"><div class="panel-title">Create note</div></div>
          <div class="form-grid">
            <div class="form-group fg-full"><label>Title *</label><input id="n-title" placeholder="Note title"></div>
            <div class="form-group fg-full"><label>Content</label><textarea id="n-content" placeholder="Write your note here..."></textarea></div>
            <div class="form-group fg-full"><label>Tags (comma separated)</label><input id="n-tags" placeholder="architecture, mcp, adk"></div>
          </div>
          <div id="note-alert" class="alert"></div>
          <div class="form-actions">
            <button class="btn btn-primary" id="note-submit-btn" onclick="createNote()">Save note</button>
            <span style="font-size:11px;color:var(--text3)">Synced to Firestore + Notion</span>
          </div>
        </div>
        <div class="panel">
          <div class="panel-head">
            <div><div class="panel-title">All notes</div><div class="panel-sub" id="notes-count-lbl">Loading...</div></div>
            <button class="btn btn-sm" onclick="loadNotes()">↻ Refresh</button>
          </div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>Title</th><th>Content</th><th>Tags</th><th>Created</th></tr></thead>
              <tbody id="notes-tbody"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- EVENTS -->
      <div id="tab-events" class="tab-pane">
        <div class="panel">
          <div class="panel-head"><div class="panel-title">Schedule event</div></div>
          <div class="form-grid cols3">
            <div class="form-group"><label>Title *</label><input id="e-title" placeholder="Event title"></div>
            <div class="form-group"><label>Start time</label><input id="e-start" type="datetime-local"></div>
            <div class="form-group"><label>Duration (minutes)</label><input id="e-dur" type="number" value="60"></div>
            <div class="form-group fg-full"><label>Description</label><input id="e-desc" placeholder="What is this event about?"></div>
          </div>
          <div id="event-alert" class="alert"></div>
          <div class="form-actions">
            <button class="btn btn-primary" id="event-submit-btn" onclick="createEvent()">Schedule event</button>
            <span style="font-size:11px;color:var(--text3)">Stored via Calendar MCP</span>
          </div>
        </div>
        <div class="panel">
          <div class="panel-head">
            <div><div class="panel-title">All events</div><div class="panel-sub" id="events-count-lbl">Loading...</div></div>
            <button class="btn btn-sm" onclick="loadEvents()">↻ Refresh</button>
          </div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>Title</th><th>Start time</th><th>Duration</th><th>Description</th><th>Status</th></tr></thead>
              <tbody id="events-tbody"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- NOTION -->
      <div id="tab-notion" class="tab-pane">
        <div class="panel">
          <div class="panel-head"><div class="panel-title">Create Notion page</div></div>
          <div class="form-grid">
            <div class="form-group fg-full"><label>Title *</label><input id="p-title" placeholder="Page title"></div>
            <div class="form-group fg-full"><label>Content</label><textarea id="p-content" placeholder="Page content..."></textarea></div>
          </div>
          <div id="notion-alert" class="alert"></div>
          <div class="form-actions">
            <button class="btn btn-primary" id="notion-submit-btn" onclick="createNotionPage()">Create page</button>
            <span style="font-size:11px;color:var(--text3)">Published via Notion MCP</span>
          </div>
        </div>
        <div class="panel">
          <div class="panel-head">
            <div><div class="panel-title">All Notion pages</div><div class="panel-sub" id="notion-count-lbl">Loading...</div></div>
            <button class="btn btn-sm" onclick="loadNotion()">↻ Refresh</button>
          </div>
          <div class="tbl-wrap">
            <table>
              <thead><tr><th>Title</th><th>Page ID</th><th>Open</th></tr></thead>
              <tbody id="notion-tbody"></tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- CHAT -->
      <div id="tab-chat" class="tab-pane">
        <div class="panel">
          <div class="panel-head">
            <div>
              <div class="panel-title">Chat with orchestrator</div>
              <div class="panel-sub">AI agent routes your request to the correct sub-agent</div>
            </div>
            <button class="btn btn-sm" onclick="clearChat()">Clear</button>
          </div>
          <div class="chat-wrap">
            <div class="chat-messages" id="chat-messages">
              <div class="msg msg-agent">Hello! I'm the orchestrator agent. I can route requests to task_agent, calendar_agent, and notes_agent. Try asking me to list your tasks or create a note.</div>
            </div>
            <div class="chat-input-row">
              <input id="chat-input" placeholder="Ask the agent anything..." onkeydown="if(event.key==='Enter')sendChat()">
              <button class="btn btn-primary" id="chat-btn" onclick="sendChat()">Send</button>
            </div>
          </div>
          <div class="quick-prompts">
            <button class="qp-btn" onclick="setChat('list all my tasks')">List tasks</button>
            <button class="qp-btn" onclick="setChat('show me all my notes')">Show notes</button>
            <button class="qp-btn" onclick="setChat('list all calendar events')">List events</button>
            <button class="qp-btn" onclick="setChat('how many tasks do I have?')">Task count</button>
            <button class="qp-btn" onclick="setChat('show me completed tasks')">Completed tasks</button>
            <button class="qp-btn" onclick="setChat('what is the system status?')">System status</button>
          </div>
        </div>
      </div>

      <!-- LINKS -->
      <div id="tab-links" class="tab-pane">
        <div class="panel">
          <div class="panel-head"><div class="panel-title">All deployed links</div></div>
          <div class="links-grid">
            <div class="link-card" onclick="openLink('https://multi-agent-system-887740208824.asia-south1.run.app/')">
              <div class="link-card-left">
                <span class="link-icon">◈</span>
                <div>
                  <div class="link-name">Dashboard</div>
                  <div class="link-url">/</div>
                </div>
              </div>
              <span class="link-arrow">↗</span>
            </div>
            <div class="link-card" onclick="openLink('https://multi-agent-system-887740208824.asia-south1.run.app/health')">
              <div class="link-card-left">
                <span class="link-icon">◉</span>
                <div>
                  <div class="link-name">Health check</div>
                  <div class="link-url">/health</div>
                </div>
              </div>
              <span class="link-arrow">↗</span>
            </div>
            <div class="link-card" onclick="openLink('https://multi-agent-system-887740208824.asia-south1.run.app/docs')">
              <div class="link-card-left">
                <span class="link-icon">⊞</span>
                <div>
                  <div class="link-name">API docs (Swagger)</div>
                  <div class="link-url">/docs</div>
                </div>
              </div>
              <span class="link-arrow">↗</span>
            </div>
            <div class="link-card" onclick="openLink('https://multi-agent-system-887740208824.asia-south1.run.app/tasks')">
              <div class="link-card-left">
                <span class="link-icon">☑</span>
                <div>
                  <div class="link-name">Tasks API</div>
                  <div class="link-url">/tasks · GET, POST</div>
                </div>
              </div>
              <span class="link-arrow">↗</span>
            </div>
            <div class="link-card" onclick="openLink('https://multi-agent-system-887740208824.asia-south1.run.app/notes')">
              <div class="link-card-left">
                <span class="link-icon">◎</span>
                <div>
                  <div class="link-name">Notes API</div>
                  <div class="link-url">/notes · GET, POST</div>
                </div>
              </div>
              <span class="link-arrow">↗</span>
            </div>
            <div class="link-card" onclick="openLink('https://multi-agent-system-887740208824.asia-south1.run.app/events')">
              <div class="link-card-left">
                <span class="link-icon">◷</span>
                <div>
                  <div class="link-name">Events API</div>
                  <div class="link-url">/events · GET, POST</div>
                </div>
              </div>
              <span class="link-arrow">↗</span>
            </div>
            <div class="link-card" onclick="openLink('https://multi-agent-system-887740208824.asia-south1.run.app/notion')">
              <div class="link-card-left">
                <span class="link-icon">⬡</span>
                <div>
                  <div class="link-name">Notion API</div>
                  <div class="link-url">/notion · GET, POST</div>
                </div>
              </div>
              <span class="link-arrow">↗</span>
            </div>
            <div class="link-card" onclick="copyText('https://multi-agent-system-887740208824.asia-south1.run.app/chat')">
              <div class="link-card-left">
                <span class="link-icon">◉</span>
                <div>
                  <div class="link-name">Chat API</div>
                  <div class="link-url">/chat · POST only · click to copy</div>
                </div>
              </div>
              <span class="link-arrow">⧉</span>
            </div>
            <div class="link-card" onclick="openLink('https://github.com/saiashirbad05/hackathon-multi-agent-project')">
              <div class="link-card-left">
                <span class="link-icon">⌥</span>
                <div>
                  <div class="link-name">GitHub repository</div>
                  <div class="link-url">saiashirbad05/hackathon-multi-agent-project</div>
                </div>
              </div>
              <span class="link-arrow">↗</span>
            </div>
            <div class="link-card" onclick="copyText('https://multi-agent-system-887740208824.asia-south1.run.app')">
              <div class="link-card-left">
                <span class="link-icon">⊙</span>
                <div>
                  <div class="link-name">Base URL</div>
                  <div class="link-url">multi-agent-system-887740208824.asia-south1.run.app · click to copy</div>
                </div>
              </div>
              <span class="link-arrow">⧉</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</div>

<!-- Copy toast -->
<div class="copy-toast" id="copy-toast">Copied to clipboard</div>

<script>
const BASE = 'https://multi-agent-system-887740208824.asia-south1.run.app';
let sessionId = 'session_' + Math.random().toString(36).substr(2,8);

const PAGES = {
  dashboard: { title: 'Dashboard', sub: 'Overview of your multi-agent system' },
  tasks:     { title: 'Tasks', sub: 'Create and manage tasks stored in Firestore' },
  notes:     { title: 'Notes', sub: 'Save notes synced to Firestore and Notion' },
  events:    { title: 'Events', sub: 'Schedule events via Calendar MCP' },
  notion:    { title: 'Notion pages', sub: 'Create and browse Notion workspace pages' },
  chat:      { title: 'Chat agent', sub: 'Natural language interface to the orchestrator' },
  links:     { title: 'API links', sub: 'All deployed endpoints and resources' }
};

function showTab(name, btn) {
  document.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  if (btn) btn.classList.add('active');
  else {
    document.querySelectorAll('.nav-item').forEach(b => {
      if (b.getAttribute('onclick') && b.getAttribute('onclick').includes("'" + name + "'")) b.classList.add('active');
    });
  }
  const p = PAGES[name] || {};
  document.getElementById('page-title').textContent = p.title || name;
  document.getElementById('page-sub').textContent = p.sub || '';
  if (name === 'tasks') loadTasks();
  if (name === 'notes') loadNotes();
  if (name === 'events') loadEvents();
  if (name === 'notion') loadNotion();
}

async function api(path, opts) {
  const r = await fetch(BASE + path, opts);
  return r.json();
}

function badge(s) {
  if (s === 'completed') return '<span class="badge badge-completed">completed</span>';
  if (s === 'in-progress') return '<span class="badge badge-progress">in progress</span>';
  return '<span class="badge badge-pending">pending</span>';
}

function fmtDate(s) {
  if (!s) return '—';
  return s.substring(0, 10);
}

function alert(id, ok, msg) {
  const el = document.getElementById(id);
  el.className = 'alert show ' + (ok ? 'alert-ok' : 'alert-err');
  el.textContent = msg;
  setTimeout(() => { el.classList.remove('show'); }, 4000);
}

function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  if (loading) {
    btn.disabled = true;
    btn.innerHTML = '<span class="loader"></span>';
  } else {
    btn.disabled = false;
    btn.textContent = btn.dataset.label || btn.textContent;
  }
}

// Init
async function init() {
  try {
    const d = await api('/health');
    if (d.status === 'healthy') {
      document.getElementById('status-dot').style.background = 'var(--green)';
      document.getElementById('status-text').textContent = 'system live';
      document.getElementById('live-text').textContent = 'live';
      document.getElementById('sys-agents').textContent = (d.agents || []).length + ' agents';
      document.getElementById('sys-mcp').textContent = (d.mcp_tools || []).join(', ');
    }
  } catch(e) {
    document.getElementById('status-text').textContent = 'offline';
    document.getElementById('status-dot').style.background = 'var(--red)';
  }
  loadDashboard();
}

async function loadDashboard() {
  try {
    const [t, n, e, p] = await Promise.all([api('/tasks'), api('/notes'), api('/events'), api('/notion')]);
    document.getElementById('s-tasks').textContent = t.count ?? '—';
    document.getElementById('s-notes').textContent = n.count ?? '—';
    document.getElementById('s-events').textContent = e.count ?? '—';
    document.getElementById('s-notion').textContent = p.count ?? '—';
    document.getElementById('nav-tasks').textContent = t.count ?? '—';
    document.getElementById('nav-notes').textContent = n.count ?? '—';
    document.getElementById('nav-events').textContent = e.count ?? '—';
    document.getElementById('nav-notion').textContent = p.count ?? '—';

    const tasks = (t.tasks || []).slice(0, 5);
    document.getElementById('dash-tasks').innerHTML = tasks.length
      ? tasks.map(x => `<tr><td><div style="font-weight:500">${x.title}</div></td><td>${badge(x.status)}</td><td style="font-family:'DM Mono',monospace;font-size:11px;color:var(--text3)">${fmtDate(x.due_date)}</td></tr>`).join('')
      : `<tr><td colspan="3"><div class="empty-state"><div class="empty-icon">☑</div>No tasks yet</div></td></tr>`;

    const notes = (n.notes || []).slice(0, 5);
    document.getElementById('dash-notes').innerHTML = notes.length
      ? notes.map(x => `<tr><td style="font-weight:500">${x.title}</td><td><div class="tag-row">${(x.tags||[]).map(t=>`<span class="tag">${t}</span>`).join('')}</div></td></tr>`).join('')
      : `<tr><td colspan="2"><div class="empty-state"><div class="empty-icon">◎</div>No notes yet</div></td></tr>`;
  } catch(e) {}
}

async function loadTasks() {
  document.getElementById('tasks-tbody').innerHTML = `<tr><td colspan="5" class="empty-state">Loading...</td></tr>`;
  try {
    const d = await api('/tasks');
    document.getElementById('tasks-count-lbl').textContent = d.count + ' total tasks';
    document.getElementById('tasks-tbody').innerHTML = (d.tasks || []).length
      ? d.tasks.map(t => `<tr>
          <td><div style="font-weight:500">${t.title}</div></td>
          <td style="color:var(--text2);max-width:180px">${t.description || '—'}</td>
          <td>${badge(t.status)}</td>
          <td style="font-family:'DM Mono',monospace;font-size:11px;color:var(--text3)">${fmtDate(t.due_date)}</td>
          <td style="font-family:'DM Mono',monospace;font-size:11px;color:var(--text3)">${fmtDate(t.created_at)}</td>
        </tr>`).join('')
      : `<tr><td colspan="5"><div class="empty-state"><div class="empty-icon">☑</div>No tasks found</div></td></tr>`;
  } catch(e) { document.getElementById('tasks-tbody').innerHTML = `<tr><td colspan="5" style="padding:20px;text-align:center;color:var(--red)">Failed to load</td></tr>`; }
}

async function loadNotes() {
  document.getElementById('notes-tbody').innerHTML = `<tr><td colspan="4" class="empty-state">Loading...</td></tr>`;
  try {
    const d = await api('/notes');
    document.getElementById('notes-count-lbl').textContent = d.count + ' total notes';
    document.getElementById('notes-tbody').innerHTML = (d.notes || []).length
      ? d.notes.map(n => `<tr>
          <td style="font-weight:500">${n.title}</td>
          <td style="color:var(--text2);max-width:220px">${(n.content||'').substring(0,80)}${n.content && n.content.length > 80 ? '...' : ''}</td>
          <td><div class="tag-row">${(n.tags||[]).map(t=>`<span class="tag">${t}</span>`).join('')}</div></td>
          <td style="font-family:'DM Mono',monospace;font-size:11px;color:var(--text3)">${fmtDate(n.created_at)}</td>
        </tr>`).join('')
      : `<tr><td colspan="4"><div class="empty-state"><div class="empty-icon">◎</div>No notes found</div></td></tr>`;
  } catch(e) {}
}

async function loadEvents() {
  document.getElementById('events-tbody').innerHTML = `<tr><td colspan="5" class="empty-state">Loading...</td></tr>`;
  try {
    const d = await api('/events');
    document.getElementById('events-count-lbl').textContent = d.count + ' total events';
    document.getElementById('events-tbody').innerHTML = (d.events || []).length
      ? d.events.map(e => `<tr>
          <td style="font-weight:500">${e.title||e.summary||'—'}</td>
          <td style="font-family:'DM Mono',monospace;font-size:11px;color:var(--text3)">${e.start_time||e.start||'—'}</td>
          <td style="color:var(--text3)">${e.duration_minutes ? e.duration_minutes + ' min' : '—'}</td>
          <td style="color:var(--text2);max-width:200px">${e.description||'—'}</td>
          <td><span class="badge badge-completed">${e.status||'scheduled'}</span></td>
        </tr>`).join('')
      : `<tr><td colspan="5"><div class="empty-state"><div class="empty-icon">◷</div>No events found</div></td></tr>`;
  } catch(e) {}
}

async function loadNotion() {
  document.getElementById('notion-tbody').innerHTML = `<tr><td colspan="3" class="empty-state">Loading...</td></tr>`;
  try {
    const d = await api('/notion');
    document.getElementById('notion-count-lbl').textContent = d.count + ' total pages';
    document.getElementById('notion-tbody').innerHTML = (d.pages || []).length
      ? d.pages.map(p => `<tr>
          <td style="font-weight:500">${p.title}</td>
          <td style="font-family:'DM Mono',monospace;font-size:11px;color:var(--text3)">${p.id}</td>
          <td><a href="https://notion.so/${p.id.replace(/-/g,'')}" target="_blank" class="btn btn-sm">Open ↗</a></td>
        </tr>`).join('')
      : `<tr><td colspan="3"><div class="empty-state"><div class="empty-icon">⬡</div>No Notion pages found</div></td></tr>`;
  } catch(e) {}
}

async function createTask() {
  const title = document.getElementById('t-title').value.trim();
  if (!title) return alert('task-alert', false, 'Title is required');
  const btn = document.getElementById('task-submit-btn');
  btn.disabled = true; btn.innerHTML = '<span class="loader"></span>';
  try {
    const d = await api('/tasks', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ title, description: document.getElementById('t-desc').value, due_date: document.getElementById('t-due').value || '2026-12-31', status: document.getElementById('t-status').value })
    });
    if (d.success) {
      alert('task-alert', true, '✓ ' + d.message);
      document.getElementById('t-title').value = '';
      document.getElementById('t-desc').value = '';
      loadTasks(); loadDashboard();
    } else { alert('task-alert', false, d.error || 'Failed to create task'); }
  } catch(e) { alert('task-alert', false, 'Network error — ' + e.message); }
  btn.disabled = false; btn.textContent = 'Create task';
}

async function createNote() {
  const title = document.getElementById('n-title').value.trim();
  if (!title) return alert('note-alert', false, 'Title is required');
  const btn = document.getElementById('note-submit-btn');
  btn.disabled = true; btn.innerHTML = '<span class="loader"></span>';
  try {
    const tags = document.getElementById('n-tags').value.split(',').map(t => t.trim()).filter(Boolean);
    const d = await api('/notes', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ title, content: document.getElementById('n-content').value, tags })
    });
    if (d.success) {
      alert('note-alert', true, '✓ ' + d.message);
      document.getElementById('n-title').value = '';
      document.getElementById('n-content').value = '';
      document.getElementById('n-tags').value = '';
      loadNotes(); loadDashboard();
    } else { alert('note-alert', false, d.error || 'Failed'); }
  } catch(e) { alert('note-alert', false, 'Network error'); }
  btn.disabled = false; btn.textContent = 'Save note';
}

async function createEvent() {
  const title = document.getElementById('e-title').value.trim();
  if (!title) return alert('event-alert', false, 'Title is required');
  const btn = document.getElementById('event-submit-btn');
  btn.disabled = true; btn.innerHTML = '<span class="loader"></span>';
  try {
    const sv = document.getElementById('e-start').value;
    const start_time = sv ? sv.replace('T',' ').substring(0,16).replace(' ','T') + ':00' : '2026-06-20T10:00:00';
    const d = await api('/events', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ title, description: document.getElementById('e-desc').value, start_time, duration_minutes: parseInt(document.getElementById('e-dur').value) || 60 })
    });
    if (d.success) {
      alert('event-alert', true, '✓ ' + d.message);
      document.getElementById('e-title').value = '';
      document.getElementById('e-desc').value = '';
      loadEvents(); loadDashboard();
    } else { alert('event-alert', false, d.error || 'Failed'); }
  } catch(e) { alert('event-alert', false, 'Network error'); }
  btn.disabled = false; btn.textContent = 'Schedule event';
}

async function createNotionPage() {
  const title = document.getElementById('p-title').value.trim();
  if (!title) return alert('notion-alert', false, 'Title is required');
  const btn = document.getElementById('notion-submit-btn');
  btn.disabled = true; btn.innerHTML = '<span class="loader"></span>';
  try {
    const d = await api('/notion', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ title, content: document.getElementById('p-content').value })
    });
    if (d.success) {
      alert('notion-alert', true, '✓ ' + d.message);
      document.getElementById('p-title').value = '';
      document.getElementById('p-content').value = '';
      loadNotion(); loadDashboard();
    } else { alert('notion-alert', false, d.error || 'Failed'); }
  } catch(e) { alert('notion-alert', false, 'Network error'); }
  btn.disabled = false; btn.textContent = 'Create page';
}

async function sendChat() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;
  input.value = '';
  const msgs = document.getElementById('chat-messages');
  msgs.innerHTML += `<div class="msg msg-user">${msg}</div>`;
  const thinking = document.createElement('div');
  thinking.className = 'msg msg-agent msg-thinking';
  thinking.textContent = 'Thinking...';
  msgs.appendChild(thinking);
  msgs.scrollTop = msgs.scrollHeight;
  const btn = document.getElementById('chat-btn');
  btn.disabled = true;
  try {
    const d = await api('/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message: msg, session_id: sessionId}) });
    thinking.remove();
    msgs.innerHTML += `<div class="msg msg-agent">${d.response || 'Done.'}</div>`;
  } catch(e) {
    thinking.remove();
    msgs.innerHTML += `<div class="msg msg-agent">Sorry, could not reach the agent.</div>`;
  }
  btn.disabled = false;
  msgs.scrollTop = msgs.scrollHeight;
}

function setChat(msg) {
  document.getElementById('chat-input').value = msg;
  sendChat();
}

function clearChat() {
  document.getElementById('chat-messages').innerHTML = '<div class="msg msg-agent">Chat cleared. How can I help you?</div>';
  sessionId = 'session_' + Math.random().toString(36).substr(2,8);
}

function openLink(url) { window.open(url, '_blank'); }

function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    const t = document.getElementById('copy-toast');
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2000);
  });
}

init();
</script>
</body>
</html>""")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)