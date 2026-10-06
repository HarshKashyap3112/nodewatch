from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.alerts.constants import AlertState, Operator
from src.models import Base, BaseMixin, utc_now


class AlertRule(Base, BaseMixin):
    __tablename__ = "alert_rules"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    server_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("servers.id", ondelete="CASCADE"), nullable=True, index=True)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    operator: Mapped[Operator] = mapped_column(SQLEnum(Operator), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # Require breaching for X seconds
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    alerts: Mapped[List["Alert"]] = relationship("Alert", back_populates="rule", cascade="all, delete-orphan")


class Alert(Base, BaseMixin):
    __tablename__ = "alerts"

    rule_id: Mapped[str] = mapped_column(String(36), ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    server_id: Mapped[str] = mapped_column(String(36), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False, index=True)
    state: Mapped[AlertState] = mapped_column(SQLEnum(AlertState), default=AlertState.TRIGGERED, nullable=False)
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    current_value: Mapped[float] = mapped_column(Float, nullable=False)
    threshold_value: Mapped[float] = mapped_column(Float, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    rule: Mapped[AlertRule] = relationship("AlertRule", back_populates="alerts")

    __table_args__ = (
        Index("idx_alerts_server_state", "server_id", "state"),
    )
