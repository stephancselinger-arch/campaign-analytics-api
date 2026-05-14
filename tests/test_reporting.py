import pytest
from datetime import datetime, timezone, date, timedelta

from app.models.events import AdEventCreate, EventType
from app.models.reports import ReportRequest
from app.services import event_store, reporting


def _today() -> date:
    return datetime.now(timezone.utc).date()


def _ts(days_ago: int = 0) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days_ago)


def _make_events() -> list[AdEventCreate]:
    base = dict(
        campaign_id="cmp_001",
        advertiser_id="adv_001",
        line_item_id="li_001",
        creative_id="cr_001",
        geo_country="USA",
        device_type="mobile",
        publisher_domain="example.com",
        placement_type="banner",
    )
    return [
        AdEventCreate(event_type=EventType.WIN, timestamp=_ts(), bid_price_cpm=5.0, clearing_price_cpm=3.5, **base),
        AdEventCreate(event_type=EventType.WIN, timestamp=_ts(), bid_price_cpm=5.0, clearing_price_cpm=4.0, **base),
        AdEventCreate(event_type=EventType.IMPRESSION, timestamp=_ts(), **base),
        AdEventCreate(event_type=EventType.IMPRESSION, timestamp=_ts(), **base),
        AdEventCreate(event_type=EventType.CLICK, timestamp=_ts(), **base),
        AdEventCreate(event_type=EventType.CONVERSION, timestamp=_ts(), conversion_value_usd=50.0, **base),
        AdEventCreate(event_type=EventType.VIDEO_START, timestamp=_ts(), **base),
        AdEventCreate(event_type=EventType.VIDEO_COMPLETE, timestamp=_ts(), **base),
        AdEventCreate(event_type=EventType.VIEWABLE, timestamp=_ts(), **base),
    ]


def test_ingest_events():
    events = _make_events()
    count = event_store.ingest(events)
    assert count == len(events)


def test_campaign_report_kpis():
    event_store.ingest(_make_events())
    today = _today()
    events = event_store.query(campaign_id="cmp_001", date_from=today, date_to=today)
    report = reporting.build_campaign_report(events, "cmp_001", "adv_001", today, today)

    assert report.impressions >= 2
    assert report.clicks >= 1
    assert report.conversions >= 1
    assert report.wins >= 2
    assert report.total_spend_usd > 0
    assert report.ctr > 0
    assert report.vcr == pytest.approx(1.0)
    assert report.viewability_rate > 0


def test_ctr_calculation():
    today = _today()
    events = event_store.query(campaign_id="cmp_001", date_from=today, date_to=today)
    report = reporting.build_campaign_report(events, "cmp_001", "adv_001", today, today)
    expected_ctr = report.clicks / report.impressions if report.impressions else 0
    assert report.ctr == pytest.approx(expected_ctr, abs=0.001)


def test_daily_breakdown():
    event_store.ingest(_make_events())
    today = _today()
    events = event_store.query(campaign_id="cmp_001", date_from=today, date_to=today)
    breakdown = reporting.build_daily_breakdown(events)
    assert len(breakdown) >= 1
    assert breakdown[0].impressions >= 0


def test_dimension_breakdown_by_country():
    event_store.ingest(_make_events())
    today = _today()
    events = event_store.query(campaign_id="cmp_001", date_from=today, date_to=today)
    breakdown = reporting.build_dimension_breakdown(events, "geo_country")
    values = [b.value for b in breakdown]
    assert "USA" in values


def test_creative_performance():
    event_store.ingest(_make_events())
    today = _today()
    events = event_store.query(campaign_id="cmp_001", date_from=today, date_to=today)
    perf = reporting.build_creative_performance(events)
    assert len(perf) >= 1
    assert perf[0].creative_id == "cr_001"


def test_spend_calculation():
    today = _today()
    events = event_store.query(campaign_id="cmp_001", date_from=today, date_to=today)
    report = reporting.build_campaign_report(events, "cmp_001", "adv_001", today, today)
    # Each win costs clearing_price_cpm / 1000. We ingested wins at 3.5 and 4.0 CPM.
    assert report.total_spend_usd > 0
    assert report.avg_cpm_usd == pytest.approx((3.5 + 4.0) / 2, rel=0.1)
