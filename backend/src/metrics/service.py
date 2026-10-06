from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.metrics.models import Metric
from src.metrics.schemas import AgentPushPayload, LatestMetricsSummary, MetricDataPoint, MetricSeriesOut
from src.metrics.utils import downsample_metrics
from src.models import utc_now
from src.servers.constants import ServerStatus
from src.servers.service import ServerService


class MetricService:
    @staticmethod
    async def ingest_agent_payload(db: AsyncSession, server_id: str, payload: AgentPushPayload) -> int:
        now = utc_now()
        metric_objects = []

        for item in payload.metrics:
            ts = item.timestamp if item.timestamp else now
            metric_objects.append(
                Metric(
                    server_id=server_id,
                    metric_name=item.name,
                    timestamp=ts,
                    value=item.value
                )
            )

        if metric_objects:
            db.add_all(metric_objects)

        # Also update server last_seen_at and metadata
        await ServerService.update_server_last_seen(
            db=db,
            server_id=server_id,
            status=ServerStatus.HEALTHY,
            hostname=payload.hostname,
            ip_address=payload.ip_address,
            os_info=payload.os_info
        )

        await db.commit()
        return len(metric_objects)

    @staticmethod
    async def query_metrics(
        db: AsyncSession,
        server_id: str,
        metric_name: str,
        start_time: datetime,
        end_time: datetime,
        max_points: int = 200
    ) -> MetricSeriesOut:
        stmt = (
            select(Metric)
            .where(
                Metric.server_id == server_id,
                Metric.metric_name == metric_name,
                Metric.timestamp >= start_time,
                Metric.timestamp <= end_time
            )
            .order_by(Metric.timestamp.asc())
        )

        result = await db.execute(stmt)
        rows = result.scalars().all()

        points = [MetricDataPoint(timestamp=m.timestamp, value=m.value) for m in rows]
        downsampled = downsample_metrics(points, max_points=max_points)

        return MetricSeriesOut(
            server_id=server_id,
            metric_name=metric_name,
            data_points=downsampled
        )

    @staticmethod
    async def get_latest_metrics_summary(db: AsyncSession, server_id: str) -> LatestMetricsSummary:
        # Get latest metric value for each metric_name for this server
        stmt = (
            select(Metric)
            .where(Metric.server_id == server_id)
            .order_by(Metric.timestamp.desc())
            .limit(100)
        )
        result = await db.execute(stmt)
        rows = result.scalars().all()

        latest_map: Dict[str, float] = {}
        last_updated: Optional[datetime] = None

        for row in rows:
            if row.metric_name not in latest_map:
                latest_map[row.metric_name] = row.value
                if last_updated is None or row.timestamp > last_updated:
                    last_updated = row.timestamp

        return LatestMetricsSummary(
            server_id=server_id,
            metrics=latest_map,
            last_updated=last_updated
        )

    @staticmethod
    async def delete_old_metrics(db: AsyncSession, retention_days: int = 30) -> int:
        cutoff_time = utc_now() - timedelta(days=retention_days)
        stmt = delete(Metric).where(Metric.timestamp < cutoff_time)
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

