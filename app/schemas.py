from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResourceIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class ResourceOut(ResourceIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


class BookingIn(BaseModel):
    resource_id: int
    guest_name: str = Field(min_length=1, max_length=120)
    start: datetime
    end: datetime


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    resource_id: int
    guest_name: str
    start: datetime
    end: datetime
    status: str
