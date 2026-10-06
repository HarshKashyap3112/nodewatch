from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.servers.constants import ServerStatus


class ServerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    os_info: Optional[str] = None


class ServerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    os_info: Optional[str] = None
    status: Optional[ServerStatus] = None


class ApiKeyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    server_id: str
    name: str
    is_revoked: bool
    last_used_at: Optional[datetime] = None
    created_at: datetime


class ApiKeyCreatedOut(ApiKeyOut):
    raw_api_key: str  # Only returned once upon key generation


class ServerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    os_info: Optional[str] = None
    status: ServerStatus
    last_seen_at: Optional[datetime] = None
    owner_id: str
    created_at: datetime
    updated_at: datetime


class ServerWithKeyOut(BaseModel):
    server: ServerOut
    api_key: ApiKeyCreatedOut
