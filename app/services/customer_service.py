from typing import List

from fastapi import HTTPException, status
from httpx import HTTPError, HTTPStatusError

from app.schemas.customers import CustomerCreate, CustomerFilter, CustomerRead
from app.services.retailcrm_client import RetailCRMClient


class CustomerService:
    def __init__(self, crm: RetailCRMClient) -> None:
        self._crm = crm

    def _map_customer(self, raw: dict) -> CustomerRead:
        phones = raw.get("phones") or []
        first_phone = (
            phones[0].get("number") if phones and isinstance(phones[0], dict) else None
        )

        created_at = raw.get("createdAt", "")
        created_at = created_at.replace(" ", "T") if created_at else ""

        mapped = {
            "id": raw.get("id"),
            "first_name": raw.get("firstName") or "",
            "last_name": raw.get("lastName"),
            "email": raw.get("email") or "",
            "phone": first_phone,
            "registered_at": created_at,
        }
        return CustomerRead.model_validate(mapped)

    async def list(self, filters: CustomerFilter) -> List[CustomerRead]:
        try:
            resp = await self._crm.get_customers(
                name=filters.first_name,
                email=filters.email,
                registered_from=(
                    filters.registered_from.isoformat()
                    if filters.registered_from
                    else None
                ),
                registered_to=(
                    filters.registered_to.isoformat() if filters.registered_to else None
                ),
                page=filters.page,
                limit=filters.limit,
            )
        except HTTPError as exc:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY, detail=f"Failed to fetch customers: {exc}"
            )

        raw_list = resp.get("customers", [])
        result: List[CustomerRead] = []
        for raw in raw_list:
            try:
                result.append(self._map_customer(raw))
            except Exception:
                continue
        return result

    async def create(self, payload: CustomerCreate) -> CustomerRead:
        data = payload.model_dump(by_alias=True, exclude_none=True)
        if phone := data.pop("phone", None):
            data["phones"] = [{"number": phone}]

        try:
            resp = await self._crm.create_customer(data)
        except HTTPStatusError as exc:
            body = {}
            try:
                body = exc.response.json()
            except Exception:
                pass
            detail = body.get("errorMsg") or body or str(exc)
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail)
        except HTTPError as exc:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY, detail=f"Failed to create customer: {exc}"
            )

        cust_id = resp.get("id")
        if not isinstance(cust_id, int):
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Unexpected create response: {resp}",
            )

        try:
            full = await self._crm.get_customer(cust_id)
        except HTTPError as exc:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch created customer: {exc}",
            )

        raw = full.get("customer", {})
        return self._map_customer(raw)
