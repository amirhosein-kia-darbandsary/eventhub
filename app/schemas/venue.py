from pydantic import BaseModel, ConfigDict, Field


class VenueBase(BaseModel):
    
    name: str = Field(min_length=1, max_length=255, examples=["Tehran Grand Hall"])
    address: str = Field(min_length=1, max_length=500, examples=["Valiasr St, Tehran"])
    city: str = Field(min_length=1, max_length=100, examples=["Tehran"])
    capacity: int = Field(gt=0, examples=[500])
    
class VenueCreate(VenueBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Tehran Grand Hall",
                    "address": "Valiasr St, Tehran",
                    "city": "Tehran",
                    "capacity": 500,
                }
            ]
        }
    )

class VenueUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    address: str | None = Field(default=None, min_length=1, max_length=500)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    capacity: int | None = Field(default=None, gt=0)
    
class VenueRead(VenueBase):
    model_config = ConfigDict(from_attributes=True)
    id: int