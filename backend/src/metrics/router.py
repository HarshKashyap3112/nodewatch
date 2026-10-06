from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.database import get_db
from src.metrics.dependencies import authenticate_agent
from src.metrics.schemas import AgentPushPayload, LatestMetricsSummary, MetricSeriesOut
from src.metrics.service import MetricService
from src.models import utc_now
from src.servers.dependencies import get_server_or_404
from src.servers.models import Server

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_metrics(
    payload: AgentPushPayload,
    server: Server = Depends(authenticate_agent),                                                                                                                                       
    db: AsyncSession = Depends(get_db)
):
    count = await MetricService.ingest_agent_payload(db, server.id, payload)
    return {"status": "accepted", "metrics_ingested": count, "server_id": server.id}


@router.get("/query", response_model=MetricSeriesOut)
async def query_metrics(
    server_id: str,
    metric_name: str,
    range: str = Query("1h", description="Time range: 1h, 6h, 24h, 7d"),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_server_or_404(server_id, db, current_user)

    now = utc_now()
    if not end_time:
        end_time = now

    if not start_time:
        if range == "1h":
            start_time = end_time - timedelta(hours=1)
        elif range == "6h":
            start_time = end_time - timedelta(hours=6)
        elif range == "24h":
            start_time = end_time - timedelta(hours=24)
        elif range == "7d":
            start_time = end_time - timedelta(days=7)
        else:
            start_time = end_time - timedelta(hours=1)

    series = await MetricService.query_metrics(
        db=db,
        server_id=server_id,
        metric_name=metric_name,
        start_time=start_time,
        end_time=end_time
    )
    return series


@router.get("/latest/{server_id}", response_model=LatestMetricsSummary)
async def get_latest_metrics(
    server_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await get_server_or_404(server_id, db, current_user)
    return await MetricService.get_latest_metrics_summary(db, server_id)
