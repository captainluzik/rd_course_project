from contextlib import asynccontextmanager
from typing import AsyncGenerator
from .config import DATABASE_URI
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine, async_sessionmaker


engine: AsyncEngine = create_async_engine(DATABASE_URI, echo=False, future=True)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionFactory() as session:
        yield session
