from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.alerts.constants import AlertState
from src.alerts.exceptions import AlertNotFoundException
from src.alerts.models import Alert, AlertRule
from src.alerts.schemas import AlertRuleIn, AlertRuleUpdate
from src.alerts.utils import evaluate_condition
from src.metrics.models import Metric
from src.models import utc_now
from src.notifications.client import NotificationClient
from src.notifications.schemas import NotificationPayload
from src.servers.constants import ServerStatus
from src.servers.models import Server


class AlertService:
    @staticmethod
    async def create_rule(db: AsyncSession, payload: AlertRuleIn) -> AlertRule:
        rule = AlertRule(
            name=payload.name,
            server_id=payload.server_id,
            metric_name=payload.metric_name,
            operator=payload.operator,
            threshold=payload.threshold,
            duration_seconds=payload.duration_seconds,
            is_enabled=payload.is_enabled,
            webhook_url=payload.webhook_url
        )
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        return rule

    @staticmethod
    async def list_rules(db: AsyncSession) -> List[AlertRule]:
        stmt = select(AlertRule).order_by(AlertRule.created_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_rule_by_id(db: AsyncSession, rule_id: str) -> Optional[AlertRule]:
        stmt = select(AlertRule).where(AlertRule.id == rule_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_rule(db: AsyncSession, rule_id: str, payload: AlertRuleUpdate) -> AlertRule:
        rule = await AlertService.get_rule_by_id(db, rule_id)
        if not rule:
            raise AlertNotFoundException("Alert rule not found")

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)

        await db.commit()
        await db.refresh(rule)
        return rule

    @staticmethod
    async def delete_rule(db: AsyncSession, rule_id: str) -> None:
        rule = await AlertService.get_rule_by_id(db, rule_id)
        if not rule:
            raise AlertNotFoundException("Alert rule not found")

        await db.delete(rule)
        await db.commit()

    @staticmethod
    async def list_alerts(
        db: AsyncSession,
        server_id: Optional[str] = None,
        state: Optional[AlertState] = None
    ) -> List[Alert]:
        stmt = select(Alert)
        if server_id:
            stmt = stmt.where(Alert.server_id == server_id)
        if state:
            stmt = stmt.where(Alert.state == state)
        stmt = stmt.order_by(Alert.triggered_at.desc())
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def evaluate_all_rules(db: AsyncSession) -> None:
        """
        Scheduled evaluation engine:
        1. Query enabled rules.
        2. Evaluate against latest metrics per server.
        3. Trigger or resolve alerts with suppression & notifications.
        """
        # Fetch enabled rules
        rules_stmt = select(AlertRule).where(AlertRule.is_enabled == True)
        rules_res = await db.execute(rules_stmt)
        rules = rules_res.scalars().all()

        # Fetch active servers
        servers_stmt = select(Server)
        servers_res = await db.execute(servers_stmt)
        servers = servers_res.scalars().all()

        for rule in rules:
            target_servers = [s for s in servers if rule.server_id is None or s.id == rule.server_id]

            for server in target_servers:
                # Get latest metric for this metric_name & server
                metric_stmt = (
                    select(Metric)
                    .where(
                        Metric.server_id == server.id,
                        Metric.metric_name == rule.metric_name
                    )
                    .order_by(Metric.timestamp.desc())
                    .limit(1)
                )
                m_res = await db.execute(metric_stmt)
                latest_metric = m_res.scalar_one_or_none()

                if not latest_metric:
                    continue

                # Check if condition breaches threshold
                is_breached = evaluate_condition(
                    current_value=latest_metric.value,
                    operator=rule.operator,
                    threshold=rule.threshold
                )

                # Query existing active alert for (rule_id, server_id)
                active_alert_stmt = (
                    select(Alert)
                    .where(
                        Alert.rule_id == rule.id,
                        Alert.server_id == server.id,
                        Alert.state == AlertState.TRIGGERED
                    )
                )
                active_res = await db.execute(active_alert_stmt)
                active_alert = active_res.scalar_one_or_none()

                now = utc_now()

                if is_breached:
                    # Update server status to WARNING or CRITICAL
                    server.status = ServerStatus.CRITICAL

                    if not active_alert:
                        # Trigger NEW alert
                        msg = f"Metric '{rule.metric_name}' breached threshold: {latest_metric.value} {rule.operator.value} {rule.threshold}"
                        new_alert = Alert(
                            rule_id=rule.id,
                            server_id=server.id,
                            state=AlertState.TRIGGERED,
                            metric_name=rule.metric_name,
                            current_value=latest_metric.value,
                            threshold_value=rule.threshold,
                            message=msg,
                            triggered_at=now
                        )
                        db.add(new_alert)
                        await db.commit()

                        # Dispatch Notification
                        await NotificationClient.send_notification(
                            NotificationPayload(
                                title=f"ALERT: {rule.name}",
                                message=msg,
                                server_name=server.name,
                                server_id=server.id,
                                metric_name=rule.metric_name,
                                current_value=latest_metric.value,
                                threshold_value=rule.threshold,
                                is_recovery=False,
                                webhook_url=rule.webhook_url
                            )
                        )
                    else:
                        # Alert is already active; suppress duplicate notification, just update current value
                        active_alert.current_value = latest_metric.value
                        await db.commit()

                else:
                    # Condition cleared
                    if active_alert:
                        # RESOLVE existing alert (FR-4.4 Recovery Notification)
                        active_alert.state = AlertState.RESOLVED
                        active_alert.resolved_at = now
                        await db.commit()

                        msg = f"Metric '{rule.metric_name}' returned to normal: {latest_metric.value}"
                        await NotificationClient.send_notification(
                            NotificationPayload(
                                title=f"RECOVERED: {rule.name}",
                                message=msg,
                                server_name=server.name,
                                server_id=server.id,
                                metric_name=rule.metric_name,
                                current_value=latest_metric.value,
                                threshold_value=rule.threshold,
                                is_recovery=True,
                                webhook_url=rule.webhook_url
                            )
                        )

                        # Restore server status if no other active alerts exist
                        remaining_active = await db.execute(
                            select(Alert).where(Alert.server_id == server.id, Alert.state == AlertState.TRIGGERED)
                        )
                        if not remaining_active.scalars().all():
                            server.status = ServerStatus.HEALTHY
                            await db.commit()

    @staticmethod
    async def check_offline_servers(db: AsyncSession, timeout_seconds: int = 120) -> int:
        """
        FR-4.6: Flag server as offline if no metrics received within configurable window.
        """
        now = utc_now()
        threshold_time = now - timedelta(seconds=timeout_seconds)

        stmt = (
            select(Server)
            .where(
                Server.status != ServerStatus.OFFLINE,
                Server.last_seen_at < threshold_time
            )
        )
        res = await db.execute(stmt)
        offline_servers = res.scalars().all()

        count = 0
        for server in offline_servers:
            server.status = ServerStatus.OFFLINE
            count += 1

        if count > 0:
            await db.commit()

        return count
