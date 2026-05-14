from fastapi import APIRouter
from app.models.events import AdEventCreate
from app.services import event_store

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/ingest")
def ingest_events(events: list[AdEventCreate]) -> dict:
    count = event_store.ingest(events)
    return {"ingested": count, "total_events": event_store.total_event_count()}
