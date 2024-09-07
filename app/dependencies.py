from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session, engine


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session
