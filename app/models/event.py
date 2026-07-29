# id venue_id title start_at ends_at status


from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Enum, ForeignKey, CheckConstraint
from datetime import datetime
import enum


class EventStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    cancelled = "cancelled"


class Event(Base):
    __tablename__ = "events"
    __table_args__=(
        CheckConstraint(sqltext="ends_at > starts_at", name="ck_events_end_after_start"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey('venues.id'))
    title: Mapped[str] = mapped_column(String(256))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus), default=EventStatus.draft)

