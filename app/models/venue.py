from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

# id name address city capacity
class Venue(Base):
    __tablename__ = "venues"
    
    id:Mapped[int] = mapped_column(primary_key=True)
    name:Mapped[str] = mapped_column(String(256))
    address:Mapped[str] = mapped_column(String(256))
    city:Mapped[str] = mapped_column(String(100), index=True)
    capacity:Mapped[int]
    