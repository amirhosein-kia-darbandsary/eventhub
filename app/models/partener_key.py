

from app.db.base import Base
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime
from datetime import datetime
from sqlalchemy.sql import func


class PartnerApiKey(Base):
    __tablename__ = "partner_api_keys"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    partner_name: Mapped[str] = mapped_column(String(length=128))
    hashed_key: Mapped[str] = mapped_column(String(length=255), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
