import uuid
from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from httpx import HTTPError

from app.schemas.orders import OrderCreate, OrderRead
from app.services.retailcrm_client import RetailCRMClient


def generate_order_number() -> str:
    return f"ORD-{datetime.now():%Y%m%d%H%M%S}-{uuid.uuid4().hex[:6].upper()}"


class OrderService:
    def __init__(self, crm: RetailCRMClient) -> None:
        self.crm = crm

    async def create(self, payload: OrderCreate) -> OrderRead:
        order_payload = {
            "orderNumber": generate_order_number(),
            "customer": {"id": payload.customer_id},
            "items": [
                {
                    "name": item.name,
                    "quantity": item.quantity,
                    "initialPrice": item.price,
                    "externalId": item.external_id,
                }
                for item in payload.items
            ],
        }

        try:
            create_resp = await self.crm.create_order(order_payload)
        except HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to create order in RetailCRM: {e}",
            )

        order_id = create_resp.get("id")
        if not isinstance(order_id, int):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Unexpected create-order response: {create_resp}",
            )

        try:
            full = await self.crm.get_order(order_id)
        except HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch created order: {e}",
            )

        raw = full.get("order", {}) or {}

        mapped = {
            "id": raw.get("id", 0),
            "orderNumber": raw.get("orderNumber") or raw.get("number") or "",
            "createdAt": raw.get("createdAt") or "",
            "customerId": (raw.get("customer") or {}).get("id") or 0,
            "items": [
                {
                    "productId": i.get("externalId") or "",
                    "name": i.get("name") or "",
                    "quantity": i.get("quantity") or 0,
                    "price": i.get("initialPrice") or 0,
                }
                for i in raw.get("items", [])
            ],
        }

        try:
            return OrderRead.model_validate(mapped)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to parse order data: {e}",
            )

    async def list_by_customer(
        self, customer_id: int, page: int = 1, limit: int = 20
    ) -> List[OrderRead]:
        try:
            resp = await self.crm.get_orders(
                customer_id=customer_id, page=page, limit=limit
            )
        except HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch orders from RetailCRM: {e}",
            )

        raw_list = resp.get("orders", [])
        result: List[OrderRead] = []

        for raw in raw_list:
            raw_items = raw.get("customProducts", [])
            mapped = {
                "id": raw.get("id", 0),
                "orderNumber": raw.get("orderNumber") or raw.get("number") or "",
                "createdAt": raw.get("createdAt") or "",
                "customerId": (raw.get("customer") or {}).get("id") or 0,
                "items": [
                    {
                        "productId": i.get("externalId") or "",
                        "name": i.get("name") or "",
                        "quantity": i.get("quantity") or 0,
                        "price": i.get("initialPrice") or 0,
                    }
                    for i in raw_items
                ],
            }
            try:
                result.append(OrderRead.model_validate(mapped))
            except Exception:
                continue

        return result
