from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

class CreateParnerApikey(BaseModel):
    partner_name: str


class ReadPartenerApiKey(BaseModel):
    id: uuid.UUID
    partner_name: str
    created_at: datetime



class UpdatePartnerApi(BaseModel):
    partner_name: Optional[str | None] = None