"""
Ad event models — the raw signals that flow into the reporting pipeline.
Every impression, click, win, and conversion gets recorded as an AdEvent.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import uuid


class EventType(str, Enum):
    IMPRESSION = "impression"
    CLICK = "click"
    WIN = "win"
    CONVERSION = "conversion"
    VIDEO_START = "video_start"
    VIDEO_FIRST_QUARTILE = "video_first_quartile"
    VIDEO_MIDPOINT = "video_midpoint"
    VIDEO_THIRD_QUARTILE = "video_third_quartile"
    VIDEO_COMPLETE = "video_complete"
    VIEWABLE = "viewable"


class AdEvent(BaseModel):
    id: str
    event_type: EventType
    timestamp: datetime

    # Campaign hierarchy
    campaign_id: str
    line_item_id: str
    creative_id: str
    advertiser_id: str

    # Auction context
    bid_price_cpm: Optional[float] = None       # what we bid
    clearing_price_cpm: Optional[float] = None  # what we paid (second price)
    auction_id: Optional[str] = None

    # Inventory context
    publisher_domain: Optional[str] = None
    placement_type: Optional[str] = None        # banner, video, native
    ad_size: Optional[str] = None               # e.g. "300x250"

    # User/device context
    user_id: Optional[str] = None
    device_type: Optional[str] = None
    geo_country: Optional[str] = None
    geo_region: Optional[str] = None

    # Conversion value
    conversion_value_usd: Optional[float] = None


class AdEventCreate(BaseModel):
    event_type: EventType
    timestamp: datetime
    campaign_id: str
    line_item_id: str
    creative_id: str
    advertiser_id: str
    bid_price_cpm: Optional[float] = None
    clearing_price_cpm: Optional[float] = None
    auction_id: Optional[str] = None
    publisher_domain: Optional[str] = None
    placement_type: Optional[str] = None
    ad_size: Optional[str] = None
    user_id: Optional[str] = None
    device_type: Optional[str] = None
    geo_country: Optional[str] = None
    geo_region: Optional[str] = None
    conversion_value_usd: Optional[float] = None


def new_event_id() -> str:
    return f"ev_{uuid.uuid4().hex[:16]}"
