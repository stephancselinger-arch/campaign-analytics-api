from fastapi import APIRouter, HTTPException
from app.models.reports import (
    CampaignReport, DailyBreakdown, DimensionBreakdown,
    CreativePerformance, ReportRequest,
)
from app.services import event_store, reporting

router = APIRouter(prefix="/reports", tags=["Reports"])

VALID_DIMENSIONS = {"geo_country", "device_type", "creative_id", "publisher_domain", "placement_type"}


@router.post("/campaign", response_model=CampaignReport)
def campaign_report(req: ReportRequest):
    if not req.campaign_id and not req.advertiser_id:
        raise HTTPException(status_code=422, detail="Provide campaign_id or advertiser_id")

    events = event_store.query(
        campaign_id=req.campaign_id,
        advertiser_id=req.advertiser_id,
        line_item_id=req.line_item_id,
        date_from=req.date_from,
        date_to=req.date_to,
    )

    return reporting.build_campaign_report(
        events=events,
        campaign_id=req.campaign_id or "all",
        advertiser_id=req.advertiser_id or "all",
        date_from=req.date_from,
        date_to=req.date_to,
    )


@router.post("/daily", response_model=list[DailyBreakdown])
def daily_breakdown(req: ReportRequest):
    events = event_store.query(
        campaign_id=req.campaign_id,
        advertiser_id=req.advertiser_id,
        line_item_id=req.line_item_id,
        date_from=req.date_from,
        date_to=req.date_to,
    )
    return reporting.build_daily_breakdown(events)


@router.post("/breakdown/{dimension}", response_model=list[DimensionBreakdown])
def dimension_breakdown(dimension: str, req: ReportRequest):
    if dimension not in VALID_DIMENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid dimension. Choose from: {sorted(VALID_DIMENSIONS)}"
        )
    events = event_store.query(
        campaign_id=req.campaign_id,
        advertiser_id=req.advertiser_id,
        date_from=req.date_from,
        date_to=req.date_to,
    )
    return reporting.build_dimension_breakdown(events, dimension)


@router.post("/creatives", response_model=list[CreativePerformance])
def creative_performance(req: ReportRequest):
    events = event_store.query(
        campaign_id=req.campaign_id,
        advertiser_id=req.advertiser_id,
        date_from=req.date_from,
        date_to=req.date_to,
    )
    return reporting.build_creative_performance(events)
