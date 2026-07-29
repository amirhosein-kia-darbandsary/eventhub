from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime,String
from datetime import datetime
from app.db.base import Base


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    provider_event_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    payload: Mapped[dict] = mapped_column(JSON)

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

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