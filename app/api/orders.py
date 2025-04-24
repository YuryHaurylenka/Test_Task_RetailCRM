from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from httpx import HTTPError

from app.schemas.orders import OrderRead, OrderCreate
from app.schemas.payments import PaymentRead, PaymentCreate
from app.services.order_service import OrderService
from app.services.payment_service import PaymentService
from app.services.retailcrm_client import RetailCRMClient

router = APIRouter(prefix="/orders", tags=["orders"])


def get_crm_client() -> RetailCRMClient:
    return RetailCRMClient()


def get_order_service(
    crm: RetailCRMClient = Depends(get_crm_client),
) -> OrderService:
    return OrderService(crm)


def get_payment_service(
    crm: RetailCRMClient = Depends(get_crm_client),
) -> PaymentService:
    return PaymentService(crm)


@router.get("/client/{client_id}", response_model=List[OrderRead])
async def list_orders_for_client(
    client_id: int,
    service: OrderService = Depends(get_order_service),
) -> List[OrderRead]:
    try:
        return await service.list_by_customer(client_id)
    except HTTPError as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch orders from RetailCRM: {exc}",
        )
    except Exception as exc:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while listing orders: {exc}",
        )


@router.post("/", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    service: OrderService = Depends(get_order_service),
) -> OrderRead:
    try:
        return await service.create(payload)
    except HTTPError as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create order in RetailCRM: {exc}",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while creating order: {exc}",
        )


@router.post(
    "/{order_id}/payments",
    response_model=PaymentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    order_id: int,
    payload: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
) -> PaymentRead:
    try:
        return await service.create(order_id, payload)
    except HTTPError as exc:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create payment in RetailCRM: {exc}",
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while creating payment: {exc}",
        )
