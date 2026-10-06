from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MetricSingleIn(BaseModel):
    name: str
    value: float
    timestamp: Optional[datetime] = None


class CheckResultSingleIn(BaseModel):
    check_name: str
    check_type: str
    status: str
    message: Optional[str] = None
    timestamp: Optional[datetime] = None


class AgentPushPayload(BaseModel):
    hostname: Optional[str] = None
    ip_address: Optional[str] = None
    os_info: Optional[str] = None
    metrics: List[MetricSingleIn] = Field(default_factory=list)
    checks: List[CheckResultSingleIn] = Field(default_factory=list)


class MetricDataPoint(BaseModel):
    timestamp: datetime
    value: float


class MetricSeriesOut(BaseModel):
    server_id: str
    metric_name: str
    data_points: List[MetricDataPoint]


class LatestMetricsSummary(BaseModel):
    server_id: str
    metrics: Dict[str, float]
    last_updated: Optional[datetime] = None
