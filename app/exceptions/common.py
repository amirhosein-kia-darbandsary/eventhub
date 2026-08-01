from .base import DomainError


class NotFoundError(DomainError):
    def __init__(self, resource: str, identifier: object):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} with id={identifier} not found")


class ConflictError(DomainError):
    def __init__(self, detail: str = "Some thing wrong happened"):
        super().__init__(detail)


class ValidationAppError(DomainError):
    def __init__(self, detail: str = "Some thing wrong happened"):
        super().__init__(detail)
