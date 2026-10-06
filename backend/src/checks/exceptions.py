from src.exceptions import NotFoundException


class CheckNotFoundException(NotFoundException):
    def __init__(self, message: str = "Check result not found"):
        super().__init__(message=message)
