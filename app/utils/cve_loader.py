import os
import git
import json
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
import aiofiles

from app.crud import CVECRUD
from app.models import CVERecord
from tqdm import tqdm
import aiohttp
from app.config import INTERNAL_HOST


class CVELoader:
    def __init__(self, repo_url: str, local_repo_path: str, session: AsyncSession):
        self.repo_url = repo_url
        self.local_repo_path = local_repo_path
        self.crud = CVECRUD(session)
        self.session = session

    def clone_or_update_repo(self):
        if not os.path.exists(self.local_repo_path):
            print("Cloning repository...")
            git.Repo.clone_from(self.repo_url, self.local_repo_path, depth=1)
        else:
            print("Updating repository...")
            repo = git.Repo(self.local_repo_path)
            repo.remotes.origin.pull()
            print("Repository updated")

    async def _load_json_files(self) -> None:
        batch_size = 1000
        batch = []

        print("Loading JSON files...")
        cves_path = os.path.join(self.local_repo_path, "cves")
        years = sorted(os.listdir(cves_path))

        for year in years:
            year_path = os.path.join(cves_path, year)
            if os.path.isdir(year_path):
                for root, _, files in os.walk(year_path):
                    print(f"Processing files in {root}")
                    for file in files:
                        if file.endswith(".json") and file != "delta.json" and file != "deltaLog.json":
                            file_path = os.path.join(root, file)
                            async with aiofiles.open(file_path, 'r') as f:
                                try:
                                    data = json.loads(await f.read())
                                    batch.append(data)
                                    if len(batch) == batch_size:
                                        await self._bulk_process_cve_data_with_api(batch)
                                        batch = []
                                except json.JSONDecodeError as e:
                                    print(f"Error decoding JSON from file {file}: {e}")

        if batch:
            # await self._bulk_process_cve_data(batch)
            await self._bulk_process_cve_data_with_api(batch)
        print(f"Loaded and processed JSON files in batches of {batch_size}")

    async def _bulk_process_cve_data(self, cve_data: List[Dict]):
        for data in tqdm(cve_data, desc="Processing data"):
            await self._process_cve_data(data)

    @staticmethod
    async def _bulk_process_cve_data_with_api(cve_data: List[Dict]):
        async with aiohttp.ClientSession() as session:
            try:
                await session.post(f"{INTERNAL_HOST}/api/v1/cve/bulk_create", json=cve_data)
            except aiohttp.ClientError as e:
                print(f"Error processing data with API: {e}")

    async def load_initial_data(self):
        self.clone_or_update_repo()
        await self._load_json_files()

    async def update_data(self):
        self.clone_or_update_repo()
        delta_path = os.path.join(self.local_repo_path, "cves", "delta.json")
        if not os.path.exists(delta_path):
            raise FileNotFoundError("Delta file not found")

        await self._process_delta_file(delta_path)

    @staticmethod
    async def _load_json(file_path: str) -> Dict:
        with open(file_path, 'r') as file:
            return json.load(file)

    async def _process_cve_record(self, file_path: str, is_new: bool) -> None:
        data = await self._load_json(file_path)
        cve_id = data.get("cveMetadata").get("cveId")

        if is_new:
            async with self.session.begin():
                await self.crud.create_cve_record_with_api(data)
        else:
            async with self.session.begin():
                await self.crud.update_cve_record(cve_id, data.get("cveMetadata"))

    async def _process_delta_file(self, delta_path: str) -> None:
        delta_data = await self._load_json(delta_path)
        actions = ["new", "updated"]
        cve_data = []
        for action in actions:
            for record in delta_data.get(action, []):
                cve_id = record.get("cveId")
                splitted_url = record.get("githubLink").split("/")
                year_dir = f"{splitted_url[-3]}/{splitted_url[-2]}"
                file_path = os.path.join(self.local_repo_path, "cves", year_dir, f"{cve_id}.json")
                file_path = await self._load_json(file_path)
                cve_data.append(file_path)
        await self._bulk_process_cve_data_with_api(cve_data)

    async def _process_cve_data(self, data: Dict):
        async with self.session.begin():
            cve_id = data.get("cveMetadata").get("cveId")

            cve_record = await self.crud.get_cve_record(cve_id)
            if not cve_record:
                cve_record = await self.crud.create_cve_record(data.get("cveMetadata"))

        await self._process_problem_types(data.get("containers", {}).get("cna", {}).get("problemTypes", []),
                                          cve_record)
        await self._process_references(data.get("containers", {}).get("cna", {}).get("references", []),
                                       cve_record)

    async def _process_problem_types(self, problem_types_data: List[Dict], cve_record: CVERecord):
        async with self.session.begin():
            for pt_data in problem_types_data:
                for description in pt_data.get("descriptions", []):
                    await self.crud.create_problem_type(description, cve_record.id)

    async def _process_references(self, references_data: List[Dict], cve_record: CVERecord):
        for ref_data in references_data:
            async with self.session.begin():
                await self.crud.create_reference(ref_data, cve_record.id)
