from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.checks.constants import CheckStatus, CheckType
from src.models import Base, BaseMixin, utc_now


class CheckResult(Base, BaseMixin):
    __tablename__ = "check_results"

    server_id: Mapped[str] = mapped_column(String(36), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False, index=True)
    check_name: Mapped[str] = mapped_column(String(100), nullable=False)
    check_type: Mapped[CheckType] = mapped_column(SQLEnum(CheckType), default=CheckType.CUSTOM, nullable=False)
    status: Mapped[CheckStatus] = mapped_column(SQLEnum(CheckStatus), nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    __table_args__ = (
        Index("idx_checks_server_name_ts", "server_id", "check_name", "timestamp"),
    )
