from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from httpx import HTTPError

from app.schemas.customers import CustomerRead, CustomerCreate, CustomerFilter
from app.services.customer_service import CustomerService
from app.services.retailcrm_client import RetailCRMClient

router = APIRouter(prefix="/customers", tags=["customers"])


def get_crm_client() -> RetailCRMClient:
    return RetailCRMClient()


def get_customer_service(
    crm: RetailCRMClient = Depends(get_crm_client),
) -> CustomerService:
    return CustomerService(crm)


@router.get("/", response_model=List[CustomerRead])
async def list_customers(
    filters: CustomerFilter = Depends(),
    service: CustomerService = Depends(get_customer_service),
):
    try:
        return await service.list(filters)
    except HTTPError as e:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch customers from RetailCRM: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while listing customers: {e}"
        )


@router.post(
    "/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED
)
async def create_customer(
    payload: CustomerCreate,
    service: CustomerService = Depends(get_customer_service),
):
    try:
        return await service.create(payload)
    except HTTPError as e:
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to create customer in RetailCRM: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error while creating customer: {e}"
        )
