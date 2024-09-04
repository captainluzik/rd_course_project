from pydantic import BaseModel, UUID4, Field
from typing import List, Optional
from datetime import datetime


class ProblemTypeSchema(BaseModel):
    id: Optional[int] = Field(None, examples=[1])
    description: Optional[str] = Field(None, examples=["description"])

    class Config:
        orm_mode = True


class ReferenceSchema(BaseModel):
    id: Optional[int] = Field(None, examples=[1])
    url: Optional[str] = Field(None, examples=["http://example.com"])
    tags: Optional[str] = Field(None, examples=["tag1, tag2"])

    class Config:
        orm_mode = True


class CVERecordSchema(BaseModel):
    id: Optional[str] = Field(None, examples=["CVE-2021-1234"])
    assigner_org_id: Optional[UUID4] = Field(None, examples=["123e4567-e89b-12d3-a456-426614174000"])
    state: Optional[str] = Field(None, examples=["PUBLIC"])
    assigner_short_name: Optional[str] = Field(None, examples=["cve"])
    date_reserved: Optional[datetime] = Field(None, examples=["2021-01-01T00:00:00"])
    date_published: Optional[datetime] = Field(None, examples=["2021-01-01T00:00:00"])
    date_updated: Optional[datetime] = Field(None, examples=["2021-01-01T00:00:00"])
    problem_types: List[ProblemTypeSchema] = []
    references: List[ReferenceSchema] = []

    class Config:
        orm_mode = True


class CreateCVERecordSchema(BaseModel):
    id: Optional[str] = Field(None, examples=["CVE-2021-1234"])
    assigner_org_id: Optional[UUID4] = Field(None, examples=["123e4567-e89b-12d3-a456-426614174000"])
    state: Optional[str] = Field(None, examples=["PUBLIC"])
    assigner_short_name: Optional[str] = Field(None, examples=["cve"])
    date_reserved: Optional[datetime] = Field(None, examples=["2021-01-01T00:00:00"])
    date_published: Optional[datetime] = Field(None, examples=["2021-01-01T00:00:00"])
    date_updated: Optional[datetime] = Field(None, examples=["2021-01-01T00:00:00"])

    class Config:
        orm_mode = True
