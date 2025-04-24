from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import Field

from .base import CamelModel


class ProductItem(CamelModel):
    name: str
    quantity: int
    price: Decimal
    external_id: Optional[str] = Field(None, alias="externalId")


class OrderCreate(CamelModel):
    customer_id: int = Field(..., alias="customerId")
    items: List[ProductItem]


class OrderRead(CamelModel):
    id: int
    order_number: str = Field(..., alias="orderNumber")
    created_at: datetime = Field(..., alias="createdAt")
    customer_id: int = Field(..., alias="customerId")
    items: List[ProductItem]
