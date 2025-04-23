from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class CustomerBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    registered_at: date


class CustomerFilter(BaseModel):
    first_name: Optional[str] = None
    email: Optional[EmailStr] = None
    registered_from: Optional[date] = None
    registered_to: Optional[date] = None
