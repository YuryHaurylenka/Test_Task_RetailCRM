from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.customers import CustomerCreate, CustomerRead
from app.schemas.payments import PaymentRead


class ProductItem(BaseModel):
    product_id: Optional[int] = None
    name: str
    quantity: int
    price: float


class OrderBase(BaseModel):
    order_number: str


class OrderCreate(OrderBase):
    customer_id: Optional[int] = None
    customer: Optional[CustomerCreate] = None
    items: List[ProductItem]


class OrderRead(OrderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    customer: CustomerRead
    items: List[ProductItem]
    payments: List[PaymentRead] = []
