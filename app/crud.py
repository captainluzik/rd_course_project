from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime
from .models import CVERecord, ProblemType, Reference


class CVECRUD:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cve_record(self, cve_id: str) -> Optional[CVERecord]:
        stmt = select(CVERecord).filter_by(id=cve_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_cve_record(self, cve_data: dict) -> CVERecord:
        exist_record = await self.get_cve_record(cve_data.get("cveId"))
        if exist_record:
            return exist_record
        cve_record = CVERecord.from_dict(cve_data)
        self.session.add(cve_record)
        return cve_record

    async def update_cve_record(self, cve_id: str, update_data: dict) -> Optional[CVERecord]:
        cve_record = await self.get_cve_record(cve_id)
        if not cve_record:
            return None

        for key, value in update_data.items():
            if key in ["date_published"]:
                try:
                    value = datetime.strptime(value, "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError(f"Invalid date format for {key}")

            setattr(cve_record, key, value)

        await self.session.commit()
        return cve_record

    async def delete_cve_record(self, cve_id: str) -> bool:
        cve_record = await self.get_cve_record(cve_id)
        if not cve_record:
            return False
        await self.session.delete(cve_record)
        await self.session.commit()
        return True

    async def get_problem_types_by_cve(self, cve_id: str) -> List[ProblemType]:
        stmt = select(ProblemType).filter_by(cve_record_id=cve_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_problem_type(self, problem_type_data: dict, cve_id: str) -> ProblemType:
        description = problem_type_data.get("description", "").strip()
        problem_type = ProblemType(description=description, cve_record_id=cve_id)
        self.session.add(problem_type)
        return problem_type

    async def delete_problem_type(self, problem_type_id: int) -> bool:
        stmt = select(ProblemType).filter_by(id=problem_type_id)
        result = await self.session.execute(stmt)
        problem_type = result.scalar_one_or_none()

        if not problem_type:
            return False

        await self.session.delete(problem_type)
        await self.session.commit()
        return True

    async def get_references_by_cve(self, cve_id: str) -> List[Reference]:
        stmt = select(Reference).filter_by(cve_record_id=cve_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_reference(self, reference_data: dict, cve_id: str) -> Reference:
        cve_record = await self.get_cve_record(cve_id)
        reference = Reference.from_dict(reference_data, cve_record)
        self.session.add(reference)
        return reference

    async def delete_reference(self, reference_id: int) -> bool:
        stmt = select(Reference).filter_by(id=reference_id)
        result = await self.session.execute(stmt)
        reference = result.scalar_one_or_none()

        if not reference:
            return False
        await self.session.delete(reference)
        await self.session.commit()
        return True
