from src.exceptions import SMPException


class InvalidMetricPayloadException(SMPException):
    def __init__(self, message: str = "Invalid metric payload format"):
        super().__init__(message=message, status_code=422)
