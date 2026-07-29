# role , crated_at
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
import uuid
from sqlalchemy import DateTime
from sqlalchemy import String, Enum
from datetime import datetime
from sqlalchemy.sql import func
import enum

# Use str here for a reason when You want to use 
# role.admin the output will be UserRole.admin 
# not 'admin' so we use str to make duck typing 
# for enums
class UserRole(str,enum.Enum):
    customer = 'customer'
    admin = 'admin'


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(256))
    full_name: Mapped[str] = mapped_column(String(256))
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.customer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
