from datetime import datetime
from typing import Optional

from pydantic import EmailStr, Field

from .base import CamelModel


class CustomerBase(CamelModel):
    first_name: str = Field(
        ...,
        description="Customer’s first name.",
        examples=["John"],
    )
    last_name: Optional[str] = Field(
        None,
        description="Customer’s surname.",
        examples=["Doe"],
    )
    email: EmailStr = Field(
        ...,
        description="Unique e-mail address.",
        examples=["john.doe@example.com"],
    )
    phone: Optional[str] = Field(
        None,
        description="Phone in international format (`+15551234567`).",
        examples=["+15551234567"],
    )


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):

    id: int = Field(
        ...,
        description="Internal CRM identifier.",
        examples=[123],
    )
    registered_at: datetime = Field(
        ...,
        description="Customer registration timestamp (ISO-8601).",
        examples=["2025-04-24T18:35:18"],
    )


class CustomerFilter(CamelModel):

    first_name: Optional[str] = Field(
        None,
        description="Substring search by first name (case-insensitive).",
        examples=["Ann"],
    )
    email: Optional[EmailStr] = Field(
        None,
        description="Exact e-mail match.",
        examples=["ann@example.com"],
    )
    registered_from: Optional[datetime] = Field(
        None,
        description="Filter ‘registered >=’ (ISO-8601).",
        examples=["2025-01-01T00:00:00"],
    )
    registered_to: Optional[datetime] = Field(
        None,
        description="Filter ‘registered <=’ (ISO-8601).",
        examples=["2025-12-31T23:59:59"],
    )
    page: int = Field(
        1,
        ge=1,
        description="Page number (starts at 1).",
        examples=[1],
    )
    limit: int = Field(
        20,
        ge=1,
        le=100,
        description="Items per page.",
        examples=[20],
    )
