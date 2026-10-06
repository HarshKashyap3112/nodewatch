from typing import Optional
from pydantic import BaseModel


class NotificationPayload(BaseModel):
    title: str
    message: str
    server_name: str
    server_id: str
    metric_name: str
    current_value: float
    threshold_value: float
    is_recovery: bool = False
    webhook_url: Optional[str] = None
    recipient_emails: Optional[str] = None
