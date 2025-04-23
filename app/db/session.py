from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import db


async def get_db() -> AsyncSession:
    """
    Dependency for providing a database session in FastAPI route handlers.
    """
    async for session in db.get_session():
        yield session
