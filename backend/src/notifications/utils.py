from src.notifications.schemas import NotificationPayload


def build_webhook_payload(payload: NotificationPayload) -> dict:
    status_str = "RECOVERED 🟢" if payload.is_recovery else "ALERT TRIGGERED 🔴"
    text = (
        f"[{status_str}] Server *{payload.server_name}*\n"
        f"Metric: `{payload.metric_name}`\n"
        f"Value: *{payload.current_value}* (Threshold: {payload.threshold_value})\n"
        f"Details: {payload.message}"
    )
    # Generic format compatible with Slack & Discord webhooks
    return {
        "text": text,
        "content": text,
        "server_id": payload.server_id,
        "is_recovery": payload.is_recovery
    }
