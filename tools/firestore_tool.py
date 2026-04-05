"""Firestore permanent storage — all agent data stored here."""
import os
from datetime import datetime, timezone
from google.cloud import firestore

_db = None

def get_db():
    global _db
    if _db is None:
        _db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "hackathon-genaiapac-cohort-1"))
    return _db

def save_task(task_id: str, title: str, description: str, due_date: str, status: str = "pending") -> dict:
    """Save a task permanently to Firestore."""
    db = get_db()
    data = {
        "task_id": task_id,
        "title": title,
        "description": description,
        "due_date": due_date,
        "status": status,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    db.collection("tasks").document(task_id).set(data)
    return {"success": True, "task_id": task_id, "message": f"Task '{title}' saved permanently to Firestore"}

def get_task(task_id: str) -> dict:
    """Get a task from Firestore."""
    db = get_db()
    doc = db.collection("tasks").document(task_id).get()
    if doc.exists:
        return {"success": True, "task": doc.to_dict()}
    return {"success": False, "message": f"Task {task_id} not found"}

def list_tasks(status_filter: str = None) -> dict:
    """List all tasks from Firestore."""
    db = get_db()
    query = db.collection("tasks")
    if status_filter:
        query = query.where("status", "==", status_filter)
    tasks = [doc.to_dict() for doc in query.stream()]
    return {"success": True, "tasks": tasks, "count": len(tasks)}

def update_task_status(task_id: str, new_status: str) -> dict:
    """Update task status in Firestore."""
    db = get_db()
    ref = db.collection("tasks").document(task_id)
    if not ref.get().exists:
        return {"success": False, "message": f"Task {task_id} not found"}
    ref.update({"status": new_status, "updated_at": datetime.now(timezone.utc).isoformat()})
    return {"success": True, "message": f"Task {task_id} updated to '{new_status}'"}

def save_note(note_id: str, title: str, content: str, tags: list = None) -> dict:
    """Save a note permanently to Firestore."""
    db = get_db()
    data = {
        "note_id": note_id,
        "title": title,
        "content": content,
        "tags": tags or [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    db.collection("notes").document(note_id).set(data)
    return {"success": True, "note_id": note_id, "message": f"Note '{title}' saved permanently to Firestore"}

def list_notes() -> dict:
    """List all notes from Firestore."""
    db = get_db()
    notes = [doc.to_dict() for doc in db.collection("notes").stream()]
    return {"success": True, "notes": notes, "count": len(notes)}
