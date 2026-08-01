from .base import DomainError


class NotFoundError(DomainError):
    def __init__(self, resource: str, identifier: object):
        self.resource = resource
        self.identifier = identifier
        super().__init__(f"{resource} with id={identifier} not found")
        
class ConflictError(DomainError):
    """برای تضاد وضعیت -- مثلاً drop کردن venue‌ای که هنوز event فعال داره."""


class ValidationAppError(DomainError):
    """برای قوانین کسب‌وکاری ورای اعتبارسنجی سطح Pydantic."""