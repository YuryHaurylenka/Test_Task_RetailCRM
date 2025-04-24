from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Order
from app.schemas.orders import OrderCreate


class OrderRepository:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, order_id: int) -> Optional[Order]:
        return await self.session.get(Order, order_id)

    async def list_by_customer(self, customer_id: int) -> Sequence[Order]:
        stmt = select(Order).where(Order.customer_id == customer_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, data: OrderCreate) -> Order:
        payload = data.model_dump(exclude={"customer", "items"})
        order = Order(**payload)
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order
