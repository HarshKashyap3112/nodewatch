from enum import Enum


class NotificationChannel(str, Enum):
    WEBHOOK = "webhook"
    EMAIL = "email"
