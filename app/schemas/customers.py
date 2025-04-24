from datetime import datetime
from typing import Optional

from pydantic import EmailStr

from .base import CamelModel


class CustomerBase(CamelModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    id: int
    registered_at: datetime


class CustomerFilter(CamelModel):
    first_name: Optional[str] = None
    email: Optional[EmailStr] = None
    registered_from: Optional[datetime] = None
    registered_to: Optional[datetime] = None
    page: int = 1
    limit: int = 20
