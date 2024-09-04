from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .config import DATABASE_URI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker


def engine():
    return create_async_engine(DATABASE_URI, echo=False, future=True)


@asynccontextmanager
async def async_session(database_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(database_engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session
