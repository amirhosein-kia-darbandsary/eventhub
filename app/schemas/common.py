from pydantic import BaseModel, ConfigDict, Field
from typing import Generic, TypeVar


T = TypeVar("T")


class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"code": "not_found", "message": "Venue with id=42 not found", "details": None}
            ]
        }
    )

    code: str = Field(description="شناسه‌ی ماشین‌خوان خطا، مثلاً 'not_found', 'conflict'")
    message: str = Field(description="پیام قابل‌خواندن برای انسان")
    details: dict | None = Field(default=None, description="اطلاعات اضافی اختیاری")


class CursorPage(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = Field(default=None, description="اگه None باشه، صفحه‌ی آخره")
    has_more: bool