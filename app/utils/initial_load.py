from cve_loader import CVELoader
from app.database import async_session
from sqlalchemy import text
import asyncio
from app.config import REPO_PATH


async def check_database():
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(text("SELECT * FROM cve_records LIMIT 1"))
            if result.fetchone():
                return False
            return True


async def initial_load():
    async with async_session() as session:
        loader = CVELoader(
            repo_url="https://github.com/CVEProject/cvelistV5",
            session=session,
            local_repo_path=REPO_PATH
        )
        await loader.load_initial_data()


if __name__ == "__main__":
    is_database_empty = asyncio.run(check_database())
    if is_database_empty:
        asyncio.run(initial_load())
        print("Initial load completed")
    else:
        print("Database is not empty")
