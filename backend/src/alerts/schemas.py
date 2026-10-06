from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.alerts.constants import AlertState, Operator


class AlertRuleIn(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    server_id: Optional[str] = None
    metric_name: str
    operator: Operator
    threshold: float
    duration_seconds: int = 0
    is_enabled: bool = True
    webhook_url: Optional[str] = None


class AlertRuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    server_id: Optional[str] = None
    metric_name: Optional[str] = None
    operator: Optional[Operator] = None
    threshold: Optional[float] = None
    duration_seconds: Optional[int] = None
    is_enabled: Optional[bool] = None
    webhook_url: Optional[str] = None


class AlertRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    server_id: Optional[str] = None
    metric_name: str
    operator: Operator
    threshold: float
    duration_seconds: int
    is_enabled: bool
    webhook_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    rule_id: str
    server_id: str
    state: AlertState
    metric_name: str
    current_value: float
    threshold_value: float
    message: str
    triggered_at: datetime
    resolved_at: Optional[datetime] = None
    created_at: datetime
