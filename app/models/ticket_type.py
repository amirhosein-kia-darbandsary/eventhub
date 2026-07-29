# id event_id price_cents totatl_quantity reservet quanti sold
# role , crated_at
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint
from datetime import datetime
from sqlalchemy import DateTime, String


class TicketType(Base):
    __tablename__ = "ticket_types"
    __table_args__ = (
        CheckConstraint('total_quantity > 0',
                        name='ck_ticket_types_total_nonneg'),
        CheckConstraint("reserved_quantity >= 0",
                        name="ck_ticket_types_reserved_nonneg"),
        CheckConstraint("sold_quantity >= 0",
                        name="ck_ticket_types_sold_nonneg"),
        CheckConstraint(
            "reserved_quantity + sold_quantity <= total_quantity",
            name="ck_ticket_types_no_overbooking",
        ),
        CheckConstraint("sales_ends_at > sales_start_at",
                        name="ck_ticket_types_end_after_start"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey('events.id'))
    price_cents: Mapped[int]
    total_quantity: Mapped[int]
    currency: Mapped[str] = mapped_column(String(255), default="Rial")
    reserved_quantity: Mapped[int] = mapped_column(default=0)
    sold_quantity: Mapped[int] = mapped_column(default=0)
    sales_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    sales_ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
