from datetime import datetime
from typing import Optional

from pydantic import Field

from .base import CamelModel


class PaymentCreate(CamelModel):
    amount: float
    comment: Optional[str] = None


class PaymentRead(CamelModel):
    id: int
    order_id: int = Field(..., alias="orderId")
    amount: float
    comment: Optional[str] = None
    created_at: datetime = Field(..., alias="createdAt")
