from src.exceptions import SMPException


class NotificationDeliveryError(SMPException):
    def __init__(self, message: str = "Failed to deliver notification"):
        super().__init__(message=message, status_code=502)
