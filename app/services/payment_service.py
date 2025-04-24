from datetime import datetime
from typing import Any, Dict, List

from fastapi import HTTPException, status
from httpx import HTTPError, HTTPStatusError

from app.schemas.payments import PaymentCreate, PaymentRead
from app.services.retailcrm_client import RetailCRMClient


class PaymentService:
    def __init__(self, crm: RetailCRMClient) -> None:
        self.crm = crm

    async def create(self, order_id: int, payload: PaymentCreate) -> PaymentRead:
        try:
            types: List[str] = await self.crm.get_payment_types()
        except HTTPError as e:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch payment types: {e}",
            )

        if not types:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail="No payment types available",
            )

        data: Dict[str, Any] = payload.model_dump(by_alias=True, exclude_none=True)
        data["order"] = {"id": order_id}
        data["type"] = types[0]

        try:
            resp = await self.crm.create_payment(data)
        except HTTPStatusError as e:
            body = {}
            try:
                body = e.response.json()
            except Exception:
                body = e.response.text
            detail = body.get("errorMsg") if isinstance(body, dict) else body
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to create payment: {detail}",
            )
        except HTTPError as e:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Network error when creating payment: {e}",
            )

        pay_id = resp.get("id")
        if not isinstance(pay_id, int):
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Unexpected create-payment response: {resp}",
            )

        try:
            full = await self.crm.get_order(order_id)
        except HTTPError as e:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch order after payment: {e}",
            )

        payments_block = (full.get("order", {}) or {}).get("payments", {})
        payments_list: List[Dict[str, Any]]
        if isinstance(payments_block, dict):
            payments_list = list(payments_block.values())
        else:
            payments_list = payments_block

        raw = next((p for p in payments_list if p.get("id") == pay_id), None)
        if not isinstance(raw, dict):
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment {pay_id} not found in order {order_id}",
            )

        ts = raw.get("createdAt") or raw.get("paidAt") or datetime.now()
        mapped = {
            "id": raw["id"],
            "orderId": order_id,
            "amount": raw.get("sum") or raw.get("amount", 0),
            "comment": raw.get("comment"),
            "createdAt": ts,
        }

        try:
            return PaymentRead.model_validate(mapped)
        except Exception as e:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to parse payment data: {e}",
            )
