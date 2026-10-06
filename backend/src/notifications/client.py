import asyncio
import logging
import smtplib
from email.message import EmailMessage
from typing import List
import httpx
from src.notifications.config import notification_settings
from src.notifications.schemas import NotificationPayload
from src.notifications.utils import build_webhook_payload

logger = logging.getLogger(__name__)


class NotificationClient:
    @staticmethod
    def _send_email_sync(subject: str, body: str, recipients: List[str]) -> bool:
        if not notification_settings.SMTP_HOST:
            return False

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = notification_settings.SENDER_EMAIL or "alerts@smp.local"
        msg["To"] = ", ".join(recipients)
        msg.set_content(body)

        try:
            with smtplib.SMTP(notification_settings.SMTP_HOST, notification_settings.SMTP_PORT, timeout=10.0) as server:
                server.starttls()
                if notification_settings.SMTP_USER and notification_settings.SMTP_PASSWORD:
                    server.login(notification_settings.SMTP_USER, notification_settings.SMTP_PASSWORD)
                server.send_message(msg)
            logger.info(f"Email notification successfully delivered to {recipients}")
            return True
        except Exception as e:
            logger.error(f"Failed to deliver email notification to {recipients}: {e}")
            return False

    @staticmethod
    async def send_email_notification(payload: NotificationPayload, recipients: List[str]) -> bool:
        status_str = "RECOVERED 🟢" if payload.is_recovery else "ALERT TRIGGERED 🔴"
        subject = f"[{status_str}] {payload.title}"
        body = (
            f"[{status_str}]\n\n"
            f"Server: {payload.server_name} ({payload.server_id})\n"
            f"Metric: {payload.metric_name}\n"
            f"Current Value: {payload.current_value} (Threshold: {payload.threshold_value})\n"
            f"Details: {payload.message}\n"
        )
        return await asyncio.to_thread(NotificationClient._send_email_sync, subject, body, recipients)

    @staticmethod
    async def send_notification(payload: NotificationPayload) -> bool:
        webhook_sent = False
        email_sent = False

        # Dispatch Webhook Notification if URL is configured
        target_url = payload.webhook_url or notification_settings.WEBHOOK_URL
        if target_url:
            try:
                body = build_webhook_payload(payload)
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(target_url, json=body)
                    if resp.is_success:
                        logger.info(f"Webhook notification delivered successfully to {target_url}")
                        webhook_sent = True
                    else:
                        logger.error(f"Failed to deliver webhook notification to {target_url}: {resp.status_code} {resp.text}")
            except Exception as e:
                logger.error(f"Error sending webhook notification to {target_url}: {e}")

        # Dispatch Email Notification if SMTP and recipients are configured
        raw_recipients = payload.recipient_emails or notification_settings.RECIPIENT_EMAILS
        if notification_settings.SMTP_HOST and raw_recipients:
            recipients = [email.strip() for email in raw_recipients.split(",") if email.strip()]
            if recipients:
                email_sent = await NotificationClient.send_email_notification(payload, recipients)

        if not target_url and not (notification_settings.SMTP_HOST and raw_recipients):
            logger.info(f"Notification skipped (no webhook URL or SMTP configured) for alert on server {payload.server_name}")
            return False

        return webhook_sent or email_sent

