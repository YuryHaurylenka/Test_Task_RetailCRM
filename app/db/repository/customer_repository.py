from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Customer
from app.schemas.customers import CustomerCreate, CustomerFilter


class CustomerRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, customer_id: int) -> Optional[Customer]:
        return await self.session.get(Customer, customer_id)

    async def list(self, filters: CustomerFilter | None = None) -> List[Customer]:
        stmt = select(Customer)
        if filters:
            if filters.first_name:
                stmt = stmt.where(Customer.first_name.ilike(f"%{filters.first_name}%"))
            if filters.email:
                stmt = stmt.where(Customer.email == filters.email)
            if filters.registered_from:
                stmt = stmt.where(Customer.registered_at >= filters.registered_from)
            if filters.registered_to:
                stmt = stmt.where(Customer.registered_at <= filters.registered_to)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, data: CustomerCreate) -> Customer:
        customer = Customer(**data.dict())
        self.session.add(customer)
        await self.session.commit()
        await self.session.refresh(customer)
        return customer
