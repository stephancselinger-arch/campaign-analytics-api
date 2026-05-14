from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import events, reports

app = FastAPI(
    title="Campaign Analytics API",
    description=(
        "Real-time ad event ingestion and campaign reporting. "
        "Tracks impressions, clicks, wins, conversions, and video events. "
        "Produces KPI reports: CTR, CVR, CPC, CPA, viewability, win rate."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/v1")
app.include_router(reports.router, prefix="/v1")


@app.get("/health")
def health():
    return {"status": "ok", "total_events": __import__("app.services.event_store", fromlist=["total_event_count"]).total_event_count()}
