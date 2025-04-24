from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import Field

from .base import CamelModel


class ProductItem(CamelModel):
    quantity: int = Field(..., ge=1, description="Item quantity (≥ 1)")
    price: Decimal = Field(..., ge=0, description="Unit price in the order currency")


class OrderCreate(CamelModel):
    customer_id: int = Field(
        ..., alias="customerId", ge=1, description="Internal customer identifier"
    )
    items: List[ProductItem] = Field(
        ...,
        min_length=1,
        description="At least one order line-item must be provided",
    )


class OrderRead(CamelModel):
    id: int
    order_number: str = Field(..., alias="orderNumber")
    created_at: datetime = Field(..., alias="createdAt")
    customer_id: int = Field(..., alias="customerId")
    items: List[ProductItem]
