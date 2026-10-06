from unittest.mock import patch, MagicMock
import pytest
from src.notifications.client import NotificationClient
from src.notifications.config import notification_settings
from src.notifications.schemas import NotificationPayload


@pytest.mark.asyncio
async def test_notification_skipped_when_unconfigured():
    payload = NotificationPayload(
        title="Test Alert",
        message="Test message",
        server_name="Server-1",
        server_id="s1",
        metric_name="cpu_usage_percent",
        current_value=90.0,
        threshold_value=80.0
    )
    # Ensure settings are clear
    with patch.object(notification_settings, "WEBHOOK_URL", None), \
         patch.object(notification_settings, "SMTP_HOST", None):
        result = await NotificationClient.send_notification(payload)
        assert result is False


@pytest.mark.asyncio
async def test_email_notification_delivery():
    payload = NotificationPayload(
        title="CPU Breach",
        message="CPU is high",
        server_name="Production-App-1",
        server_id="srv-101",
        metric_name="cpu_usage_percent",
        current_value=95.5,
        threshold_value=80.0,
        is_recovery=False
    )

    with patch.object(notification_settings, "SMTP_HOST", "smtp.test.com"), \
         patch.object(notification_settings, "RECIPIENT_EMAILS", "admin@example.com, ops@example.com"), \
         patch("smtplib.SMTP") as mock_smtp_cls:

        mock_smtp_inst = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_smtp_inst

        result = await NotificationClient.send_notification(payload)

        assert result is True
        assert mock_smtp_inst.starttls.called
        assert mock_smtp_inst.send_message.called
