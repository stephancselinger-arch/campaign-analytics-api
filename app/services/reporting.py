"""
Reporting engine — aggregates raw events into KPIs.

Takes a list of AdEvents and computes the metrics that matter:
impressions, clicks, spend, CTR, CVR, CPC, CPA, win rate, viewability.
"""

from collections import defaultdict
from datetime import date
from typing import Optional

from app.models.events import AdEvent, EventType
from app.models.reports import (
    CampaignReport, DailyBreakdown, DimensionBreakdown, CreativePerformance
)


def _safe_divide(numerator: float, denominator: float) -> float:
    return round(numerator / denominator, 4) if denominator > 0 else 0.0


def build_campaign_report(
    events: list[AdEvent],
    campaign_id: str,
    advertiser_id: str,
    date_from: date,
    date_to: date,
) -> CampaignReport:
    impressions = sum(1 for e in events if e.event_type == EventType.IMPRESSION)
    clicks = sum(1 for e in events if e.event_type == EventType.CLICK)
    wins = sum(1 for e in events if e.event_type == EventType.WIN)
    conversions = sum(1 for e in events if e.event_type == EventType.CONVERSION)
    video_starts = sum(1 for e in events if e.event_type == EventType.VIDEO_START)
    video_completions = sum(1 for e in events if e.event_type == EventType.VIDEO_COMPLETE)
    viewable = sum(1 for e in events if e.event_type == EventType.VIEWABLE)

    spend_events = [e for e in events if e.clearing_price_cpm is not None and e.event_type == EventType.WIN]
    total_spend = sum((e.clearing_price_cpm or 0) / 1000 for e in spend_events)
    avg_cpm = _safe_divide(sum(e.clearing_price_cpm or 0 for e in spend_events), len(spend_events))

    bid_events = [e for e in events if e.bid_price_cpm is not None]
    avg_bid = _safe_divide(sum(e.bid_price_cpm or 0 for e in bid_events), len(bid_events))

    conversion_value = sum(e.conversion_value_usd or 0 for e in events if e.event_type == EventType.CONVERSION)

    return CampaignReport(
        campaign_id=campaign_id,
        advertiser_id=advertiser_id,
        date_from=date_from,
        date_to=date_to,
        impressions=impressions,
        clicks=clicks,
        wins=wins,
        conversions=conversions,
        video_starts=video_starts,
        video_completions=video_completions,
        viewable_impressions=viewable,
        total_spend_usd=round(total_spend, 4),
        avg_cpm_usd=round(avg_cpm, 4),
        avg_clearing_price_usd=round(avg_bid, 4),
        ctr=_safe_divide(clicks, impressions),
        cvr=_safe_divide(conversions, clicks),
        cpc_usd=_safe_divide(total_spend, clicks),
        cpa_usd=_safe_divide(total_spend, conversions),
        vcr=_safe_divide(video_completions, video_starts),
        viewability_rate=_safe_divide(viewable, impressions),
        win_rate=_safe_divide(wins, len(bid_events)),
    )


def build_daily_breakdown(events: list[AdEvent]) -> list[DailyBreakdown]:
    by_date: dict[date, list[AdEvent]] = defaultdict(list)
    for ev in events:
        by_date[ev.timestamp.date()].append(ev)

    rows = []
    for day in sorted(by_date):
        day_events = by_date[day]
        impressions = sum(1 for e in day_events if e.event_type == EventType.IMPRESSION)
        clicks = sum(1 for e in day_events if e.event_type == EventType.CLICK)
        conversions = sum(1 for e in day_events if e.event_type == EventType.CONVERSION)
        spend_events = [e for e in day_events if e.clearing_price_cpm and e.event_type == EventType.WIN]
        spend = sum((e.clearing_price_cpm or 0) / 1000 for e in spend_events)
        avg_cpm = _safe_divide(sum(e.clearing_price_cpm or 0 for e in spend_events), len(spend_events))

        rows.append(DailyBreakdown(
            date=day,
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            spend_usd=round(spend, 4),
            ctr=_safe_divide(clicks, impressions),
            cpm_usd=round(avg_cpm, 4),
        ))
    return rows


def build_dimension_breakdown(events: list[AdEvent], dimension: str) -> list[DimensionBreakdown]:
    by_value: dict[str, list[AdEvent]] = defaultdict(list)
    for ev in events:
        val = getattr(ev, dimension, None) or "unknown"
        by_value[str(val)].append(ev)

    rows = []
    for value, dim_events in sorted(by_value.items(), key=lambda x: -len(x[1])):
        impressions = sum(1 for e in dim_events if e.event_type == EventType.IMPRESSION)
        clicks = sum(1 for e in dim_events if e.event_type == EventType.CLICK)
        conversions = sum(1 for e in dim_events if e.event_type == EventType.CONVERSION)
        spend = sum((e.clearing_price_cpm or 0) / 1000 for e in dim_events if e.clearing_price_cpm and e.event_type == EventType.WIN)

        rows.append(DimensionBreakdown(
            dimension=dimension,
            value=value,
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            spend_usd=round(spend, 4),
            ctr=_safe_divide(clicks, impressions),
        ))
    return rows


def build_creative_performance(events: list[AdEvent]) -> list[CreativePerformance]:
    by_creative: dict[str, list[AdEvent]] = defaultdict(list)
    for ev in events:
        by_creative[ev.creative_id].append(ev)

    rows = []
    for creative_id, cr_events in sorted(by_creative.items()):
        impressions = sum(1 for e in cr_events if e.event_type == EventType.IMPRESSION)
        clicks = sum(1 for e in cr_events if e.event_type == EventType.CLICK)
        conversions = sum(1 for e in cr_events if e.event_type == EventType.CONVERSION)
        video_starts = sum(1 for e in cr_events if e.event_type == EventType.VIDEO_START)
        video_completions = sum(1 for e in cr_events if e.event_type == EventType.VIDEO_COMPLETE)
        viewable = sum(1 for e in cr_events if e.event_type == EventType.VIEWABLE)
        spend = sum((e.clearing_price_cpm or 0) / 1000 for e in cr_events if e.clearing_price_cpm and e.event_type == EventType.WIN)

        rows.append(CreativePerformance(
            creative_id=creative_id,
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            spend_usd=round(spend, 4),
            ctr=_safe_divide(clicks, impressions),
            vcr=_safe_divide(video_completions, video_starts),
            viewability_rate=_safe_divide(viewable, impressions),
        ))
    return rows
