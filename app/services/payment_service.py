from app.schemas.payments import PaymentCreate, PaymentRead
from app.services.retailcrm_client import RetailCRMClient


class PaymentService:
    def __init__(self, crm_client: RetailCRMClient) -> None:
        self.crm_client = crm_client

    async def create(self, order_id: int, payload: PaymentCreate) -> PaymentRead:
        data = payload.model_dump()
        data["orderId"] = order_id
        resp = await self.crm_client.create_payment(data)
        return PaymentRead.model_validate(resp["payment"])
