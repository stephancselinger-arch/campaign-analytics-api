"""
Event store — ingests ad events and indexes them for fast reporting queries.

In production this would be ClickHouse or BigQuery. Here we use an in-memory
list with simple aggregation. The interface is intentionally the same so you
can swap the backend without changing the routers.
"""

from collections import defaultdict
from datetime import datetime, timezone, date
from typing import Optional

from app.models.events import AdEvent, AdEventCreate, EventType, new_event_id


_events: list[AdEvent] = []


def ingest(batch: list[AdEventCreate]) -> int:
    for ev in batch:
        _events.append(AdEvent(id=new_event_id(), **ev.model_dump()))
    return len(batch)


def query(
    campaign_id: Optional[str] = None,
    advertiser_id: Optional[str] = None,
    line_item_id: Optional[str] = None,
    creative_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    event_types: Optional[list[EventType]] = None,
) -> list[AdEvent]:
    results = _events

    if campaign_id:
        results = [e for e in results if e.campaign_id == campaign_id]
    if advertiser_id:
        results = [e for e in results if e.advertiser_id == advertiser_id]
    if line_item_id:
        results = [e for e in results if e.line_item_id == line_item_id]
    if creative_id:
        results = [e for e in results if e.creative_id == creative_id]
    if event_types:
        results = [e for e in results if e.event_type in event_types]
    if date_from:
        results = [e for e in results if e.timestamp.date() >= date_from]
    if date_to:
        results = [e for e in results if e.timestamp.date() <= date_to]

    return results


def total_event_count() -> int:
    return len(_events)
