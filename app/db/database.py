from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


class Database:
    def __init__(self, db_url: str, echo: bool = False):
        """
        Database helper class for managing async SQLAlchemy sessions.
        """
        self.engine = create_async_engine(
            db_url,
            future=True,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
        self.scoped_session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )

    async def get_session(self):
        """
        Dependency для FastAPI for creating async sessions.
        """
        async with self.session_factory() as session:
            yield session
            await session.close()


db = Database(
    db_url=settings.db_url,
    echo=settings.db_echo,
)