from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class CustomerBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(w.capitalize() for w in parts[1:])


class CustomerRead(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str]
    email: str
    phone: Optional[str]
    registered_at: datetime

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
    )


class CustomerFilter(BaseModel):
    first_name: Optional[str] = None
    email: Optional[EmailStr] = None
    registered_from: Optional[datetime] = None
    registered_to: Optional[datetime] = None
    page: int = 1
    limit: int = 20
