from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.checks.constants import CheckStatus, CheckType


class CheckResultIn(BaseModel):
    check_name: str
    check_type: CheckType
    status: CheckStatus
    message: Optional[str] = None
    timestamp: Optional[datetime] = None


class CheckResultOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    server_id: str
    check_name: str
    check_type: CheckType
    status: CheckStatus
    message: Optional[str] = None
    timestamp: datetime
