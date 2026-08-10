from pydantic import BaseModel, Field, ConfigDict
import uuid
from datetime import datetime
from app.models.reserve import ReservationStatus


class ReservationCreate(BaseModel):
    ticket_type_id: int
    quantity: int = Field(gt=0, examples=[2])
    
    
class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    ticket_type_id: int
    quantity: int = Field(gt=0, examples=[2])
    id: int
    user_id: uuid.UUID  # 
    status: ReservationStatus
    expires_at: datetime

