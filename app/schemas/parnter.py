from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class CreateParnerApikey(BaseModel):
    partner_name: str = Field(min_length=4, max_length=256)


class ReadPartenerApiKey(BaseModel):
    id: uuid.UUID
    partner_name: str
    created_at: datetime


class UpdatePartnerApi(BaseModel):
    partner_name: Optional[str | None] = Field(min_length=4, max_length=256)
