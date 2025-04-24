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
        first_name: Optional[str] = None,
        email: Optional[str] = None,
        registered_from: Optional[str] = None,
        registered_to: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {"site": self._site, "page": page, "limit": limit}
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
        form = {"site": self._site, "customer": json.dumps(data, default=str)}
        response = await self._client.post(
            "/customers/create",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()

    async def get_customer(self, customer_id: int) -> Dict[str, Any]:
        response = await self._client.get(
            f"/customers/{customer_id}",
            params={"by": "id", "site": self._site},
        )
        response.raise_for_status()
        return response.json()

    async def get_orders(
        self,
        customer_id: int,
        page: int = 1,
        limit: int = 20,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "site": self._site,
            "filter[customerId]": customer_id,
            "page": page,
            "limit": limit,
        }
        response = await self._client.get("/orders", params=params)
        response.raise_for_status()
        return response.json()

    async def create_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        form = {"site": self._site, "order": json.dumps(data, default=str)}
        response = await self._client.post(
            "/orders/create",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()

    async def get_order(self, order_id: int) -> Dict[str, Any]:
        response = await self._client.get(
            f"/orders/{order_id}",
            params={"by": "id", "site": self._site},
        )
        response.raise_for_status()
        return response.json()

    async def get_products(self, external_id: str) -> List[Dict[str, Any]]:
        response = await self._client.get(
            "/store/products",
            params={"site": self._site, "filter[externalId]": external_id},
        )
        response.raise_for_status()
        return response.json().get("products", [])

    async def batch_create_products(self, products: List[Dict[str, Any]]) -> List[int]:
        payload = [
            {
                "externalId": p["externalId"],
                "name": p["name"],
                "catalogId": 1,
                "type": "product",
                "initialPrice": p["initialPrice"],
            }
            for p in products
        ]
        form = {"site": self._site, "products": json.dumps(payload, default=str)}
        response = await self._client.post(
            "/store/products/batch/create",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json().get("addedProducts", [])

    async def get_payment_types(self) -> List[str]:
        response = await self._client.get(
            "/reference/payment-types", params={"site": self._site}
        )
        response.raise_for_status()
        data = response.json().get("paymentTypes", {})
        if isinstance(data, dict):
            return [
                info.get("code") for info in data.values() if isinstance(info, dict)
            ]
        if isinstance(data, list):
            return [info.get("code") for info in data if isinstance(info, dict)]
        return []

    async def create_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        form = {"site": self._site, "payment": json.dumps(data, default=str)}
        response = await self._client.post(
            "/orders/payments/create",
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            body = (
                response.json()
                if response.headers.get("content-type", "").startswith(
                    "application/json"
                )
                else response.text
            )
            raise httpx.HTTPStatusError(
                f"{response.status_code}: {body}",
                request=error.request,
                response=response,
            )
        return response.json()
