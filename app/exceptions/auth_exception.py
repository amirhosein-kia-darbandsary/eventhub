from app.exceptions.base import DomainError

class InvalidCredentialsError(DomainError):
    def __init__(self):
        super().__init__("Invalid email or password")


class InvalidTokenError(DomainError):
    def __init__(self, detail: str = "Invalid or expired token"):
        super().__init__(detail)


class ForbiddenError(DomainError):
    def __init__(self, detail: str = "You don't have permission to perform this action"):
        super().__init__(detail)