from app.dependencies import get_session
from app.models import CVERecord
from app.schemas import CVERecordSchema, CreateCVERecordSchema
from typing import Any
from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import Response, JSONResponse
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import CVECRUD
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import joinedload
from fastapi.exceptions import HTTPException

router = APIRouter(
    prefix='/api/v1/cve',
    tags=['cves'],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}}
)

SessionDepends = Depends(get_session)


@router.get('/ping')
async def ping():
    return Response(status_code=status.HTTP_200_OK, content="pong")


@router.get('/list', response_model=Page[CVERecordSchema])
async def list_cves(
        start_date: Optional[str] = Query(None, description="Filter CVEs by start date in the format YYYY-MM-DD."),
        end_date: Optional[str] = Query(None, description="Filter CVEs by end date in the format YYYY-MM-DD."),
        pk: Optional[str] = Query(None, description="Filter CVEs by partial ID."),
        session: AsyncSession = SessionDepends) -> Page[CVERecordSchema]:
    """
    Retrieve a paginated list of CVE records.

    - **start_date**: Optional start date to filter CVEs. Format should be YYYY-MM-DD.
    - **end_date**: Optional end date to filter CVEs. Format should be YYYY-MM-DD.
    - **pk**: Optional partial ID to filter CVEs.
    """
    stmt = select(CVERecord)

    if start_date:
        try:
            start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d")
            stmt = stmt.filter(CVERecord.date_published >= start_date_parsed)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")

    if end_date:
        try:
            end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d")
            stmt = stmt.filter(CVERecord.date_published <= end_date_parsed)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")

    if pk:
        stmt = stmt.filter(CVERecord.id.ilike(f"%{pk}%"))

    return await paginate(session, stmt)


@router.get("/{cve_id}", response_model=CVERecordSchema)
async def get_cve_record(cve_id: str, session: AsyncSession = SessionDepends) -> CVERecordSchema:
    """
    Retrieve a CVE record by its ID.

    - **cve_id**: The ID of the CVE record to retrieve.
    """
    stmt = select(CVERecord).options(
        joinedload(CVERecord.problem_types),
        joinedload(CVERecord.references)
    ).filter_by(id=cve_id)
    result = await session.execute(stmt)
    cve_record = result.scalars().first()
    if cve_record:
        return cve_record
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.post('/create', response_model=CreateCVERecordSchema)
async def create_cve(cve_data: Dict, session: AsyncSession = SessionDepends) -> CVERecordSchema:
    """
    Create a new CVE record.

    - **cve_data**: The data for the new CVE record.
    """
    exist_record = await session.get(CVERecord, cve_data.get("id"))
    if exist_record:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "CVE already exists"})
    cve_record = CVERecord.from_api(cve_data)
    session.add(cve_record)
    await session.commit()
    return cve_record


@router.patch("/{cve_id}", response_model=CreateCVERecordSchema)
async def update_cve_record(cve_id: str, update_data: Dict, session: AsyncSession = SessionDepends) -> CVERecordSchema:
    """
    Update an existing CVE record by its ID.

    - **cve_id**: The ID of the CVE record to update.
    - **update_data**: The data to update.
    """
    cve_record = await CVECRUD(session).update_cve_record(cve_id, update_data)
    if cve_record:
        return cve_record
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.delete("/{cve_id}")
async def delete_cve_record(cve_id: str, session: AsyncSession = SessionDepends) -> Any:
    """
    Delete a CVE record by its ID.

    - **cve_id**: The ID of the CVE record to delete.
    """
    result = await CVECRUD(session).delete_cve_record(cve_id)
    if result:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


@router.post("/bulk_create")
async def bulk_create_cve_records(cve_data: List[Dict], session: AsyncSession = SessionDepends) -> JSONResponse:
    """
    Bulk create CVE records.

    - **cve_data**: A list of CVE records to create.
    """
    cve_records = await CVECRUD(session).bulk_create_all(cve_data)
    return JSONResponse(content={"detail": f"{len(cve_records)} records created."})
