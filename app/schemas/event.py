from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field,  model_validator
from app.models.event import EventStatus


class BaseEvent(BaseModel):
    title: str = Field(examples=['Dinner party'])
    starts_at: datetime = Field(examples=["2026-09-01T19:00:00Z"])
    ends_at: datetime = Field(examples=["2026-09-01T23:00:00Z"])


class EventCreate(BaseEvent):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "venue_id": 1,
                    "title": "EventHub Launch Night",
                    "starts_at": "2026-09-01T19:00:00Z",
                    "ends_at": "2026-09-01T22:00:00Z",
                }
            ]
        }
    )
    venue_id: int

    @model_validator(mode="after")
    def check_ends_after_starts(self) -> "EventCreate":
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class EventRead(BaseEvent):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: EventStatus
    venue_id: int


class EventUpdate(BaseModel):
    venue_id: int | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    status: EventStatus | None = None
