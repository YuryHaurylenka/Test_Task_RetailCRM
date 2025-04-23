from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


def to_camel(s: str) -> str:
    parts = s.split("_")
    return parts[0] + "".join(w.capitalize() for w in parts[1:])


class ProductItem(BaseModel):
    name: str
    quantity: int
    price: Decimal
    external_id: Optional[str] = Field(None, alias="externalId")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
    )


class OrderCreate(BaseModel):
    customer_id: int = Field(..., alias="customerId")
    items: List[ProductItem]

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
    )


class OrderRead(BaseModel):
    id: int
    order_number: str = Field(..., alias="orderNumber")
    created_at: datetime = Field(..., alias="createdAt")
    customer_id: int = Field(..., alias="customerId")
    items: List[ProductItem]

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
    )
