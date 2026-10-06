from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.alerts.exceptions import AlertNotFoundException
from src.alerts.models import AlertRule
from src.alerts.service import AlertService
from src.database import get_db


async def verify_rule_ownership(
    rule_id: str,
    db: AsyncSession = Depends(get_db)
) -> AlertRule:
    rule = await AlertService.get_rule_by_id(db, rule_id)
    if not rule:
        raise AlertNotFoundException("Alert rule not found")
    return rule
