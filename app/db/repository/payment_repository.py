from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Payment
from app.schemas.payments import PaymentCreate


class PaymentRepository:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, payment_id: int) -> Optional[Payment]:
        return await self.session.get(Payment, payment_id)

    async def list_by_order(self, order_id: int) -> list[Payment]:
        stmt = select(Payment).where(Payment.order_id == order_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, data: PaymentCreate) -> Payment:
        payment = Payment(**data.model_dump())
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment
