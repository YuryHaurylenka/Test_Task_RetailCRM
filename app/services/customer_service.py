from typing import List, Optional

from fastapi import HTTPException, status
from httpx import HTTPError

from app.schemas.customers import CustomerRead, CustomerCreate, CustomerFilter
from app.services.retailcrm_client import RetailCRMClient


class CustomerService:
    def __init__(self, crm: RetailCRMClient) -> None:
        self.crm = crm

    async def list(self, filters: CustomerFilter) -> List[CustomerRead]:
        try:
            resp = await self.crm.get_customers(
                first_name=filters.first_name,
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
        except HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch customers: {e}",
            )

        raw_list = resp.get("customers", [])
        result: List[CustomerRead] = []

        for raw in raw_list:
            phone: Optional[str] = (raw.get("phones") or [None])[0]

            raw_dt: Optional[str] = raw.get("createdAt")
            if raw_dt:
                dt_str = raw_dt.replace(" ", "T")
            else:
                dt_str = None

            mapped = {
                "id": raw.get("id"),
                "first_name": raw.get("firstName") or "",
                "last_name": raw.get("lastName"),
                "email": raw.get("email") or "",
                "phone": phone,
                "registered_at": dt_str,
            }

            try:
                customer = CustomerRead.model_validate(mapped)
            except Exception as e:
                continue

            result.append(customer)

        return result

    async def create(self, payload: CustomerCreate) -> CustomerRead:

        try:
            resp_email = await self.crm.get_customers(email=payload.email, limit=1)
        except HTTPError as e:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to check existing email: {e}",
            )
        if resp_email.get("customers"):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="A customer with this email already exists",
            )

        if payload.phone:
            try:
                resp_phone = await self.crm.get_customers(page=1, limit=100)
            except HTTPError as e:
                raise HTTPException(
                    status.HTTP_502_BAD_GATEWAY,
                    detail=f"Failed to check existing phone: {e}",
                )
            for raw in resp_phone.get("customers", []):
                phones: list[str] = raw.get("phones") or []
                if payload.phone in phones:
                    raise HTTPException(
                        status.HTTP_400_BAD_REQUEST,
                        detail="A customer with this phone number already exists",
                    )

        try:
            resp = await self.crm.create_customer(payload.model_dump())
        except HTTPError as e:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY, detail=f"Failed to create customer: {e}"
            )

        cust_id = resp.get("id")
        if not isinstance(cust_id, int):
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Unexpected create response: {resp}",
            )

        try:
            full = await self.crm.get_customer(cust_id)
        except HTTPError as e:
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to fetch created customer: {e}",
            )

        raw = full.get("customer")
        if not isinstance(raw, dict):
            raise HTTPException(
                status.HTTP_502_BAD_GATEWAY,
                detail=f"Invalid get-customer response: {full}",
            )

        first_phone = (raw.get("phones") or [None])[0]
        mapped = {
            "id": raw.get("id"),
            "first_name": raw.get("firstName"),
            "last_name": raw.get("lastName"),
            "email": raw.get("email"),
            "phone": first_phone,
            "registered_at": raw.get("createdAt"),
        }
        return CustomerRead.model_validate(mapped)
