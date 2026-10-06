from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models import Base, BaseMixin
from src.servers.constants import ServerStatus


class Server(Base, BaseMixin):
    __tablename__ = "servers"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hostname: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    os_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[ServerStatus] = mapped_column(
        SQLEnum(ServerStatus),
        default=ServerStatus.OFFLINE,
        nullable=False
    )
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    api_keys: Mapped[List["AgentApiKey"]] = relationship("AgentApiKey", back_populates="server", cascade="all, delete-orphan")


class AgentApiKey(Base, BaseMixin):
    __tablename__ = "agent_api_keys"

    server_id: Mapped[str] = mapped_column(String(36), ForeignKey("servers.id", ondelete="CASCADE"), nullable=False)
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), default="default", nullable=False)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    server: Mapped[Server] = relationship("Server", back_populates="api_keys")
