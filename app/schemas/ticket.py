from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator
from datetime import datetime


class TicketTypeCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"event_id": 1,
                          "price_cents": 15000,
                          "total_quantity": 100,
                          "sales_start_at": "2026-09-01T19:00:00Z",
                          "sales_ends_at": "2026-09-01T20:00:00Z"}]
        }
    )

    event_id: int
    price_cents: int = Field(ge=0, examples=[15000])
    total_quantity: int = Field(ge=0, examples=[100])
    sales_start_at: datetime = Field(examples=["2026-09-01T19:00:00Z"])
    sales_ends_at: datetime = Field(examples=["2026-09-01T19:00:00Z"])

    @model_validator(mode="after")
    def check_ends_after_starts(self) -> "TicketTypeCreate":
        if self.sales_ends_at <= self.sales_start_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class TicketTypeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    price_cents: int
    total_quantity: int
    reserved_quantity: int
    sold_quantity: int

    @computed_field
    @property
    def available(self) -> int:
        return self.total_quantity - self.reserved_quantity - self.sold_quantity
