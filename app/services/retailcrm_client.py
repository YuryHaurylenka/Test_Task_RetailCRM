import json
from typing import Any, Dict, Optional, List

import httpx

from app.core.config import settings


class RetailCRMClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            base_url=f"{settings.retailcrm_base_url}/api/v5",
            headers={"X-API-KEY": settings.retailcrm_api_key},
            timeout=10.0,
        )
        self._site=settings.retailcrm_site

    async def get_customers(
        self,
        first_name: Optional[str] = None,
        email: Optional[str] = None,
        registered_from: Optional[str] = None,
        registered_to: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"page": page, "limit": limit}
        if first_name:
            params["filter[firstName]"] = first_name
        if email:
            params["filter[email]"] = email
        if registered_from:
            params["filter[createdAtFrom]"] = registered_from
        if registered_to:
            params["filter[createdAtTo]"] = registered_to

        response = await self._client.get("/customers", params=params)
        response.raise_for_status()
        return response.json()

    async def create_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        form = {"customer": json.dumps(data)}
        response = await self._client.post(
            "/customers/create",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()

    async def get_customer(self, customer_id: int) -> dict:
        response = await self._client.get(
            f"/customers/{customer_id}", params={"by": "id"}
        )
        response.raise_for_status()
        return response.json()

    async def get_orders(
        self,
        customer_id: int,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        params = {
            "filter[customerId]": customer_id,
            "page": page,
            "limit": limit,
        }
        response = await self._client.get("/orders", params=params)
        response.raise_for_status()
        return response.json()

    async def create_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        form = {
            "site": settings.retailcrm_site,
            "order": json.dumps(order, default=str),
        }
        resp = await self._client.post(
            "/orders/create",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_order(self, order_id: int) -> dict:
        r = await self._client.get(
            f"/orders/{order_id}",
            params={"by": "id"}
        )
        r.raise_for_status()
        return r.json()

    async def create_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        form = {"payment": json.dumps(data, default=str)}
        response = await self._client.post(
            "/orders/payment/create",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()

    async def get_products(self, external_id: str) -> List[Dict[str, Any]]:
        r = await self._client.get(
            "/store/products", params={"filter[externalId]": external_id}
        )
        r.raise_for_status()
        data = r.json()
        return data.get("products", [])

    async def batch_create_products(self, products: list[dict]) -> list[int]:
        form = {
            "site": settings.retailcrm_site,
            "products": json.dumps(products, default=str),
        }
        r = await self._client.post(
            "/store/products/batch/create",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        r.raise_for_status()
        data = r.json()
        return data.get("addedProducts", [])
