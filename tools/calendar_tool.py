"""Google Calendar tool — graceful fallback if auth not available."""
import os
from datetime import datetime, timedelta

def create_calendar_event(title: str, description: str, start_time: str, duration_minutes: int = 60) -> dict:
    """Create a Google Calendar event."""
    try:
        from googleapiclient.discovery import build
        from google.auth import default
        credentials, _ = default(scopes=["https://www.googleapis.com/auth/calendar"])
        service = build("calendar", "v3", credentials=credentials)
        start_dt = datetime.fromisoformat(start_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": "Asia/Kolkata"},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": "Asia/Kolkata"}
        }
        result = service.events().insert(calendarId="primary", body=event).execute()
        return {
            "success": True,
            "event_id": result["id"],
            "event_link": result.get("htmlLink", ""),
            "message": f"Calendar event '{title}' created"
        }
    except Exception as e:
        # Fallback — store in Firestore as scheduled event
        from google.cloud import firestore
        import uuid
        db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
        event_id = f"event_{str(uuid.uuid4())[:8]}"
        db.collection("calendar_events").document(event_id).set({
            "event_id": event_id,
            "title": title,
            "description": description,
            "start_time": start_time,
            "duration_minutes": duration_minutes,
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat(),
            "note": "Stored in Firestore — Google Calendar OAuth not available in this environment"
        })
        return {
            "success": True,
            "event_id": event_id,
            "message": f"Event '{title}' scheduled and stored in Firestore database",
            "fallback": True
        }


def list_upcoming_events(max_results: int = 10) -> dict:
    """List upcoming calendar events."""
    try:
        from googleapiclient.discovery import build
        from google.auth import default
        credentials, _ = default(scopes=["https://www.googleapis.com/auth/calendar"])
        service = build("calendar", "v3", credentials=credentials)
        now = datetime.utcnow().isoformat() + "Z"
        result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = []
        for e in result.get("items", []):
            start = e["start"].get("dateTime", e["start"].get("date"))
            events.append({"id": e["id"], "title": e["summary"], "start": start})
        return {"success": True, "events": events, "count": len(events)}
    except Exception as e:
        # Fallback — read from Firestore
        from google.cloud import firestore
        db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
        events = [doc.to_dict() for doc in db.collection("calendar_events").stream()]
        return {"success": True, "events": events, "count": len(events), "fallback": True}


def delete_calendar_event(event_id: str) -> dict:
    """Delete a calendar event."""
    try:
        from googleapiclient.discovery import build
        from google.auth import default
        credentials, _ = default(scopes=["https://www.googleapis.com/auth/calendar"])
        service = build("calendar", "v3", credentials=credentials)
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return {"success": True, "message": f"Event {event_id} deleted"}
    except Exception as e:
        from google.cloud import firestore
        db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT"))
        db.collection("calendar_events").document(event_id).delete()
        return {"success": True, "message": f"Event {event_id} removed from Firestore"}
