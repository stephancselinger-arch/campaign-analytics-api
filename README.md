# Campaign Analytics API

Real-time ad event ingestion and campaign reporting for programmatic advertising. Tracks every impression, click, win, conversion, and video event — then aggregates them into the KPIs that AdTech teams live by: CTR, CVR, CPC, CPA, viewability, win rate, and spend.

## Features

- **Event Ingestion** — batch ingest any ad event type (impression, click, win, conversion, video quartiles, viewable)
- **Campaign Reports** — full KPI summary for any campaign or advertiser over a date range
- **Daily Breakdown** — day-by-day spend, impressions, clicks, CTR, CPM
- **Dimension Breakdown** — slice performance by geo, device type, creative, publisher, or placement
- **Creative Performance** — CTR, VCR, viewability per creative
- **Spend Tracking** — CPM vs clearing price, total spend, CPC, CPA

## How It Fits Into the Stack

```
DSP Bidder Engine  ──win notice──▶  Campaign Analytics API
Creative Trafficking API            (stores all ad events)
Audience Segmentation Service              │
                                    ┌──────▼──────┐
                                    │  Reports UI  │
                                    │  (future)    │
                                    └─────────────┘
```

Every time the DSP Bidder wins an auction, it sends an event here. Every impression served, every click, every conversion — all flow into this service and become reportable.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8003 --reload
```

API docs: http://localhost:8003/docs

## API Reference

### Events

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/events/ingest` | Batch ingest ad events |

### Reports

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/reports/campaign` | Full KPI report for a campaign |
| `POST` | `/v1/reports/daily` | Day-by-day breakdown |
| `POST` | `/v1/reports/breakdown/{dimension}` | Slice by geo, device, creative, publisher |
| `POST` | `/v1/reports/creatives` | Creative-level performance |

**Valid dimensions:** `geo_country`, `device_type`, `creative_id`, `publisher_domain`, `placement_type`

## Example: Ingest Events

```json
POST /v1/events/ingest
[
  {
    "event_type": "win",
    "timestamp": "2026-05-14T10:00:00Z",
    "campaign_id": "cmp_abc123",
    "line_item_id": "li_xyz789",
    "creative_id": "cr_001",
    "advertiser_id": "adv_001",
    "bid_price_cpm": 5.00,
    "clearing_price_cpm": 3.75,
    "geo_country": "USA",
    "device_type": "mobile",
    "publisher_domain": "publisher.com"
  },
  {
    "event_type": "impression",
    "timestamp": "2026-05-14T10:00:00Z",
    "campaign_id": "cmp_abc123",
    "line_item_id": "li_xyz789",
    "creative_id": "cr_001",
    "advertiser_id": "adv_001"
  }
]
```

## Example: Campaign Report

```json
POST /v1/reports/campaign
{
  "campaign_id": "cmp_abc123",
  "date_from": "2026-05-01",
  "date_to": "2026-05-14"
}
```

Response:
```json
{
  "campaign_id": "cmp_abc123",
  "impressions": 142850,
  "clicks": 1285,
  "conversions": 64,
  "wins": 142850,
  "total_spend_usd": 535.69,
  "avg_cpm_usd": 3.75,
  "ctr": 0.009,
  "cvr": 0.0498,
  "cpc_usd": 0.4168,
  "cpa_usd": 8.37,
  "win_rate": 0.312,
  "viewability_rate": 0.68,
  "vcr": 0.71
}
```

## KPI Glossary

| KPI | Formula | What it tells you |
|-----|---------|-------------------|
| CTR | clicks / impressions | How engaging the creative is |
| CVR | conversions / clicks | How well the landing page converts |
| CPC | spend / clicks | Cost efficiency per click |
| CPA | spend / conversions | Cost per acquisition |
| VCR | video completes / starts | Video engagement quality |
| Win Rate | wins / bids | Bidding competitiveness |
| Viewability | viewable / impressions | Ad quality / placement quality |

## Running Tests

```bash
pytest tests/ -v
```

## Production Considerations

| Component | Dev (current) | Production |
|-----------|--------------|------------|
| Event store | In-memory list | ClickHouse / BigQuery |
| Query speed | O(n) scan | Columnar indexes, sub-second |
| Scale | Thousands of events | Billions of events/day |
| Retention | Process lifetime | Configurable (90 days default) |

## Tech Stack

- **FastAPI** — async REST framework
- **Pydantic v2** — event validation
- Python 3.12+

<!-- Last updated: 2026-05-14 -->

<!-- Last updated: 2026-05-15 -->

<!-- Last updated: 2026-05-17 -->

<!-- Last updated: 2026-05-19 -->

<!-- Last updated: 2026-05-21 -->

<!-- Last updated: 2026-05-23 -->

<!-- Last updated: 2026-05-25 -->

<!-- Last updated: 2026-05-27 -->

<!-- Last updated: 2026-05-29 -->

<!-- Last updated: 2026-05-31 -->

<!-- Last updated: 2026-06-01 -->

<!-- Last updated: 2026-06-03 -->

<!-- Last updated: 2026-06-05 -->

<!-- Last updated: 2026-06-07 -->

<!-- Last updated: 2026-06-09 -->

<!-- Last updated: 2026-06-11 -->

<!-- Last updated: 2026-06-13 -->
