from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.alerts.constants import AlertState
from src.alerts.dependencies import verify_rule_ownership
from src.alerts.models import AlertRule
from src.alerts.schemas import AlertOut, AlertRuleIn, AlertRuleOut, AlertRuleUpdate
from src.alerts.service import AlertService
from src.auth.dependencies import get_current_user
from src.auth.models import User
from src.database import get_db

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# Rules Endpoints
@router.post("/rules", response_model=AlertRuleOut, status_code=status.HTTP_201_CREATED)
async def create_alert_rule(
    payload: AlertRuleIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rule = await AlertService.create_rule(db, payload)
    return AlertRuleOut.model_validate(rule)


@router.get("/rules", response_model=List[AlertRuleOut])
async def list_alert_rules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    rules = await AlertService.list_rules(db)
    return [AlertRuleOut.model_validate(r) for r in rules]


@router.get("/rules/{rule_id}", response_model=AlertRuleOut)
async def get_alert_rule(rule: AlertRule = Depends(verify_rule_ownership)):
    return AlertRuleOut.model_validate(rule)


@router.patch("/rules/{rule_id}", response_model=AlertRuleOut)
async def update_alert_rule(
    payload: AlertRuleUpdate,
    rule: AlertRule = Depends(verify_rule_ownership),
    db: AsyncSession = Depends(get_db)
):
    updated = await AlertService.update_rule(db, rule.id, payload)
    return AlertRuleOut.model_validate(updated)


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert_rule(
    rule: AlertRule = Depends(verify_rule_ownership),
    db: AsyncSession = Depends(get_db)
):
    await AlertService.delete_rule(db, rule.id)


# Alerts Feed Endpoints
@router.get("", response_model=List[AlertOut])
async def list_alerts(
    server_id: Optional[str] = None,
    state: Optional[AlertState] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    alerts = await AlertService.list_alerts(db, server_id=server_id, state=state)
    return [AlertOut.model_validate(a) for a in alerts]
