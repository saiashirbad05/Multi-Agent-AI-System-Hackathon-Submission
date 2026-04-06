# Multi-Agent-AI-System-Project-Hackathon

A production-ready multi-agent AI system built with **Google ADK**, **Firestore**, **Notion MCP**, and **Google Calendar MCP**, deployed on **Cloud Run**.

## 🏗️ Architecture
## 🤖 Agents

| Agent | Role |
|---|---|
| `orchestrator` | Primary agent — routes requests to sub-agents |
| `task_agent` | Creates, lists, updates tasks in Firestore |
| `calendar_agent` | Manages calendar events |
| `notes_agent` | Saves notes to Firestore and Notion |

## 🔧 MCP Tools

| Tool | Integration |
|---|---|
| Firestore MCP | Permanent task and note storage |
| Notion MCP | External page creation and sync |
| Google Calendar MCP | Event scheduling |

## 🌐 Live API

**Base URL:** `https://multi-agent-system-887740208824.asia-south1.run.app`

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Live dashboard |
| `/health` | GET | System status |
| `/tasks` | GET/POST | List or create tasks |
| `/notes` | GET/POST | List or create notes |
| `/events` | GET/POST | List or create calendar events |
| `/notion` | GET/POST | List or create Notion pages |
| `/chat` | POST | Natural language agent interface |
| `/docs` | GET | Auto-generated API docs |

## 🚀 Quick Demo
```bash
# Create a task
curl -X POST https://multi-agent-system-887740208824.asia-south1.run.app/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"My Task","description":"Demo task","due_date":"2026-06-20","status":"pending"}'

# Chat with agent
curl -X POST https://multi-agent-system-887740208824.asia-south1.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"list all my tasks","session_id":"demo"}'
```

## 🛠️ Tech Stack

- **Google ADK** — Agent orchestration framework
- **Gemini 2.0 Flash Lite** — LLM for agent reasoning
- **Firestore** — Permanent NoSQL database
- **Notion API** — External notes MCP
- **Google Calendar API** — Schedule MCP
- **FastAPI** — REST API framework
- **Cloud Run** — Serverless deployment
- **GCP** — Cloud infrastructure

## 📦 Setup
```bash
git clone https://github.com/saiashirbad05/hackathon-multi-agent-project.git
cd hackathon-multi-agent-project
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your keys
python3 main.py
```

## 🔑 Environment Variables
```env
GOOGLE_API_KEY=your_gemini_api_key
GOOGLE_CLOUD_PROJECT=your_gcp_project
NOTION_API_TOKEN=secret_your_notion_token
NOTION_PAGE_ID=your_notion_page_id
```
