import json
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings


class RetailCRMClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=f"{settings.retailcrm_base_url}/api/v5",
            headers={"X-API-KEY": settings.retailcrm_api_key},
            timeout=10.0,
        )
        self._site = settings.retailcrm_site

    async def get_customers(
        self,
        name: Optional[str] = None,
        email: Optional[str] = None,
        registered_from: Optional[str] = None,
        registered_to: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "site": self._site,
            "page": page,
            "limit": limit,
        }
        if name:
            params["filter[name]"] = name
        if email:
            params["filter[email]"] = email
        if registered_from:
            params["filter[createdAtFrom]"] = registered_from
        if registered_to:
            params["filter[createdAtTo]"] = registered_to

        resp = await self._client.get("/customers", params=params)
        resp.raise_for_status()
        return resp.json()

    async def create_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        form = {"site": self._site, "customer": json.dumps(data, default=str)}
        resp = await self._client.post(
            "/customers/create",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_customer(self, customer_id: int) -> Dict[str, Any]:
        resp = await self._client.get(
            f"/customers/{customer_id}",
            params={"by": "id", "site": self._site},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_orders(
        self, customer_id: int, page: int = 1, limit: int = 20
    ) -> Dict[str, Any]:
        params = {
            "site": self._site,
            "filter[customerId]": customer_id,
            "page": page,
            "limit": limit,
        }
        resp = await self._client.get("/orders", params=params)
        resp.raise_for_status()
        return resp.json()

    async def create_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        form = {"site": self._site, "order": json.dumps(data, default=str)}
        resp = await self._client.post(
            "/orders/create",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_order(self, order_id: int) -> Dict[str, Any]:
        resp = await self._client.get(
            f"/orders/{order_id}", params={"by": "id", "site": self._site}
        )
        resp.raise_for_status()
        return resp.json()

    async def get_products(self) -> List[Dict[str, Any]]:
        resp = await self._client.get("/store/products", params={"site": self._site})
        resp.raise_for_status()
        return resp.json().get("products", [])

    async def get_payment_types(self) -> List[str]:
        resp = await self._client.get(
            "/reference/payment-types", params={"site": self._site}
        )
        resp.raise_for_status()
        data = resp.json().get("paymentTypes", {})
        if isinstance(data, dict):
            return [
                info.get("code") for info in data.values() if isinstance(info, dict)
            ]
        if isinstance(data, list):
            return [item.get("code") for item in data if isinstance(item, dict)]
        return []

    async def create_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        form = {"site": self._site, "payment": json.dumps(data, default=str)}
        resp = await self._client.post(
            "/orders/payments/create",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as err:
            body = (
                resp.json()
                if resp.headers.get("content-type", "").startswith("application/json")
                else resp.text
            )
            raise httpx.HTTPStatusError(
                f"{resp.status_code}: {body}", request=err.request, response=resp
            )
        return resp.json()
