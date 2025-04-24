from datetime import datetime
from typing import Optional

from pydantic import Field

from .base import CamelModel


class PaymentCreate(CamelModel):
    amount: float = Field(..., gt=0, description="Payment amount in order currency")
    comment: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Optional short comment or reference",
    )


class PaymentRead(CamelModel):
    id: int
    order_id: int = Field(..., alias="orderId", ge=1)
    amount: float
    comment: Optional[str] = None
    created_at: datetime = Field(..., alias="createdAt")
