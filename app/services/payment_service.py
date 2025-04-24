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
            payment_types: List[str] = await self.crm.get_payment_types()
        except HTTPError as error:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch payment types: {error}",
            )
        if not payment_types:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail="No payment types available",
            )

        data: Dict[str, Any] = {
            "order": {"id": order_id},
            "amount": payload.amount,
            "type": payment_types[0],
        }
        if payload.comment:
            data["comment"] = payload.comment

        try:
            resp = await self.crm.create_payment(data)
        except HTTPStatusError as error:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to create payment: {error}",
            )
        except HTTPError as error:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Network error when creating payment: {error}",
            )

        pay_id = resp.get("id")
        if not isinstance(pay_id, int):
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Unexpected create-payment response: {resp}",
            )

        try:
            full = await self.crm.get_order(order_id)
        except HTTPError as error:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch order after payment: {error}",
            )

        payments_block = full.get("order", {}).get("payments") or {}
        payments_list = (
            list(payments_block.values())
            if isinstance(payments_block, dict)
            else payments_block
        )
        raw = next((p for p in payments_list if p.get("id") == pay_id), None)
        if not isinstance(raw, dict):
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Payment {pay_id} not found in order {order_id}",
            )

        ts = raw.get("createdAt") or raw.get("paidAt") or datetime.utcnow()
        mapped = {
            "id": raw["id"],
            "orderId": order_id,
            "amount": raw.get("sum") or raw.get("amount") or 0,
            "comment": raw.get("comment"),
            "createdAt": ts,
        }

        try:
            return PaymentRead.model_validate(mapped)
        except Exception as error:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to parse payment data: {error}",
            )
