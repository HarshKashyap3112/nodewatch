from datetime import datetime
from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from src.models import Base, BaseMixin, utc_now


class Metric(Base, BaseMixin):
    __tablename__ = "metrics"

    server_id: Mapped[str] = mapped_column(String(36), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)

    __table_args__ = (
        Index("idx_metrics_server_name_ts", "server_id", "metric_name", "timestamp"),
    )
