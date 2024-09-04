import os
import git
import json
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict

from app.crud import CVECRUD
from app.models import CVERecord
from tqdm import tqdm


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

    def _load_json_files(self) -> List[dict]:
        cve_data = []
        print("Loading JSON files...")
        for root, _, files in os.walk(os.path.join(self.local_repo_path, "cves")):
            for file in files:
                if file.endswith(".json") and file != "delta.json" and file != "deltaLog.json":
                    with open(os.path.join(root, file), 'r') as f:
                        try:
                            data = json.load(f)
                            cve_data.append(data)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON from file {file}: {e}")
        print(f"Loaded {len(cve_data)} JSON files")
        return cve_data

    async def load_initial_data(self):
        self.clone_or_update_repo()
        cve_data = self._load_json_files()
        print("Processing data...")
        for data in tqdm(cve_data):
            await self._process_cve_data(data)

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
                await self.crud.create_cve_record(data.get("cveMetadata"))
        else:
            async with self.session.begin():
                await self.crud.update_cve_record(cve_id, data.get("cveMetadata"))

    async def _process_delta_file(self, delta_path: str) -> None:
        delta_data = await self._load_json(delta_path)
        actions = ["new", "updated"]
        for action in actions:
            for record in delta_data.get(action, []):
                cve_id = record.get("cveId")
                splitted_url = record.get("githubLink").split("/")
                year_dir = f"{splitted_url[-3]}/{splitted_url[-2]}"
                file_path = os.path.join(self.local_repo_path, "cves", year_dir, f"{cve_id}.json")
                await self._process_cve_record(file_path, is_new=True if action == "new" else False)

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
