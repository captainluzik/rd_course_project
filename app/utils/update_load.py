import os
from .cve_loader import CVELoader
from app.database import async_session
from app.config import REPO_PATH


async def update_load():
    async with async_session() as session:
        loader = CVELoader(
            repo_url="https://github.com/CVEProject/cvelistV5",
            session=session,
            local_repo_path=REPO_PATH
        )
        await loader.update_data()


if __name__ == "__main__":
    import asyncio

    asyncio.run(update_load())
