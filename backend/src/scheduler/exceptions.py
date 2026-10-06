from src.exceptions import SMPException


class SchedulerJobError(SMPException):
    def __init__(self, message: str = "Scheduler job failed"):
        super().__init__(message=message, status_code=500)
