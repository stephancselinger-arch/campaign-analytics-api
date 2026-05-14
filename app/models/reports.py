from typing import Optional
from pydantic import BaseModel
from datetime import date


class CampaignReport(BaseModel):
    campaign_id: str
    advertiser_id: str
    date_from: date
    date_to: date

    # Volume
    impressions: int = 0
    clicks: int = 0
    wins: int = 0
    conversions: int = 0

    # Video
    video_starts: int = 0
    video_completions: int = 0
    viewable_impressions: int = 0

    # Spend
    total_spend_usd: float = 0.0
    avg_cpm_usd: float = 0.0
    avg_clearing_price_usd: float = 0.0

    # Derived KPIs
    ctr: float = 0.0          # click-through rate
    cvr: float = 0.0          # conversion rate
    cpc_usd: float = 0.0      # cost per click
    cpa_usd: float = 0.0      # cost per acquisition
    vcr: float = 0.0          # video completion rate
    viewability_rate: float = 0.0
    win_rate: float = 0.0


class DailyBreakdown(BaseModel):
    date: date
    impressions: int
    clicks: int
    conversions: int
    spend_usd: float
    ctr: float
    cpm_usd: float


class DimensionBreakdown(BaseModel):
    dimension: str            # e.g. "geo_country", "device_type", "creative_id"
    value: str
    impressions: int
    clicks: int
    conversions: int
    spend_usd: float
    ctr: float


class CreativePerformance(BaseModel):
    creative_id: str
    impressions: int
    clicks: int
    conversions: int
    spend_usd: float
    ctr: float
    vcr: float
    viewability_rate: float


class ReportRequest(BaseModel):
    campaign_id: Optional[str] = None
    advertiser_id: Optional[str] = None
    line_item_id: Optional[str] = None
    date_from: date
    date_to: date
    breakdown: Optional[str] = None   # "daily", "geo_country", "device_type", "creative_id"
