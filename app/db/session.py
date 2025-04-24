from typing import Any, AsyncGenerator

from app.db.database import db


async def get_db() -> AsyncGenerator[Any, Any]:
    """
    Dependency for providing a database session in FastAPI route handlers.
    """
    async for session in db.get_session():
        yield session
