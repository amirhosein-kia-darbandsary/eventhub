from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, String, Enum
from datetime import datetime
from app.db.base import Base
import uuid
import enum
from sqlalchemy import func



class WebHookEventStatus(str, enum.Enum):
    received = "received"    # recently arrieved
    processed = "processed"  # Successful
    dead_letter = "dead_letter"  # after retrying has failed


class WebHookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    provider_event_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    payload: Mapped[str] = mapped_column(String)

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    status: Mapped[WebHookEventStatus] = mapped_column(Enum(WebHookEventStatus),
                                                       default=WebHookEventStatus.processed)


class ApiKey(Base):
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True)

    partner_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    key_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    scopes: Mapped[str]

    rate_limit_tier: Mapped[int]


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id: Mapped[int] = mapped_column(primary_key=True)

    key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    enabled: Mapped[bool] = mapped_column(default=False)

    rollout_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )
