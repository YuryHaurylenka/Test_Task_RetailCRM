import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import HTTPException, status
from httpx import HTTPError

from app.schemas.orders import OrderCreate, OrderRead
from app.services.retailcrm_client import RetailCRMClient


def generate_order_number() -> str:
    return f"ORD-{datetime.utcnow():%Y%m%d%H%M%S}-{uuid.uuid4().hex[:6].upper()}"


class OrderService:
    def __init__(self, crm: RetailCRMClient) -> None:
        self._crm = crm

    def _map_raw(self, raw: Dict[str, Any]) -> OrderRead:
        items_src = raw.get("customProducts") or raw.get("items") or []
        mapped: Dict[str, Any] = {
            "id": raw.get("id", 0),
            "orderNumber": raw.get("orderNumber") or raw.get("number", ""),
            "createdAt": raw.get("createdAt", ""),
            "customerId": (raw.get("customer") or {}).get("id", 0),
            "items": [
                {
                    "productId": item.get("externalId", ""),
                    "name": item.get("name", ""),
                    "quantity": item.get("quantity", 0),
                    "price": item.get("initialPrice", 0),
                }
                for item in items_src
            ],
        }
        try:
            return OrderRead.model_validate(mapped)
        except Exception as exc:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to parse order data: {exc}",
            )

    async def create(self, payload: OrderCreate) -> OrderRead:
        payload_data: Dict[str, Any] = {
            "orderNumber": generate_order_number(),
            "customer": {"id": payload.customer_id},
            "customProducts": [
                {
                    "externalId": item.external_id,
                    "name": item.name,
                    "quantity": item.quantity,
                    "initialPrice": item.price,
                }
                for item in payload.items
            ],
        }
        try:
            response = await self._crm.create_order(payload_data)
        except HTTPError as exc:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Error creating order in RetailCRM: {exc}",
            )

        order_id = response.get("id")
        if not isinstance(order_id, int):
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Invalid create-order response: {response}",
            )

        try:
            order_data = await self._crm.get_order(order_id)
        except HTTPError as exc:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Error fetching created order: {exc}",
            )

        raw_order = order_data.get("order") or {}
        return self._map_raw(raw_order)

    async def list_by_customer(
        self, customer_id: int, page: int = 1, limit: int = 20
    ) -> List[OrderRead]:
        try:
            summary = await self._crm.get_orders(
                customer_id=customer_id, page=page, limit=limit
            )
        except HTTPError as exc:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Error fetching orders list: {exc}",
            )

        orders: List[OrderRead] = []
        for entry in summary.get("orders", []):
            oid = entry.get("id")
            if not isinstance(oid, int):
                continue
            try:
                order_data = await self._crm.get_order(oid)
            except HTTPError:
                continue

            raw_order = order_data.get("order") or {}
            try:
                orders.append(self._map_raw(raw_order))
            except HTTPException:
                continue

        return orders
