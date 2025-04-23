from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict
from app.db.models import PaymentMethod, PaymentStatus


class PaymentBase(BaseModel):
    amount: Decimal
    method: PaymentMethod


class PaymentCreate(PaymentBase):
    order_id: int


class PaymentRead(PaymentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: PaymentStatus
    paid_at: datetime

    class Config:
        orm_mode = True
