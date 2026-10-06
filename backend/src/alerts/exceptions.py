from src.exceptions import NotFoundException, SMPException


class AlertNotFoundException(NotFoundException):
    def __init__(self, message: str = "Alert or alert rule not found"):
        super().__init__(message=message)


class AlertRuleInvalidException(SMPException):
    def __init__(self, message: str = "Invalid alert rule definition"):
        super().__init__(message=message, status_code=422)
