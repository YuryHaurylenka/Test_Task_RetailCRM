import uuid
from datetime import datetime
from typing import Any, Dict, List

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
        order_payload: Dict[str, Any] = {
            "number": generate_order_number(),
            "customer": {"id": payload.customer_id},
            "items": [
                {
                    "quantity": item.quantity,
                    "initialPrice": item.price,
                }
                for item in payload.items
            ],
        }
        try:
            resp = await self.crm.create_order(order_payload)
        except HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error creating order in RetailCRM: {exc}",
            )

        order_id = resp.get("id")
        if not isinstance(order_id, int):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Unexpected create-order response: {resp}",
            )

        try:
            full = await self.crm.get_order(order_id)
        except HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error fetching created order: {exc}",
            )

        raw = full.get("order", {}) or {}
        return self._map_raw(raw)

    async def list_by_customer(
        self, customer_id: int, page: int = 1, limit: int = 20
    ) -> List[OrderRead]:
        try:
            summary = await self.crm.get_orders(
                customer_id=customer_id, page=page, limit=limit
            )
        except HTTPError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error fetching orders list: {exc}",
            )

        orders: List[OrderRead] = []
        for entry in summary.get("orders", []):
            oid = entry.get("id")
            if not isinstance(oid, int):
                continue
            try:
                full = await self.crm.get_order(oid)
            except HTTPError:
                continue

            raw = full.get("order", {}) or {}
            try:
                orders.append(self._map_raw(raw))
            except HTTPException:
                continue

        return orders

    def _map_raw(self, raw: Dict[str, Any]) -> OrderRead:
        items = raw.get("items", []) or []
        mapped: Dict[str, Any] = {
            "id": raw.get("id", 0),
            "orderNumber": raw.get("number", ""),
            "createdAt": raw.get("createdAt", ""),
            "customerId": (raw.get("customer") or {}).get("id", 0),
            "items": [
                {
                    "quantity": i.get("quantity", 0),
                    "price": i.get("initialPrice") or i.get("price") or 0,
                }
                for i in items
            ],
        }
        try:
            return OrderRead.model_validate(mapped)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to parse order data: {exc}",
            )
