from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from app.models.candidate import SkillKind


class ResumeBase(BaseModel):
    object_key: str
    filename: str
    mime_type: str
    size_bytes: int


class ResumeCreate(ResumeBase):
    pass


class Resume(ResumeBase):
    id: UUID
    candidate_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateSkillBase(BaseModel):
    skill: str
    kind: SkillKind
    level: Optional[int] = Field(None, ge=1, le=5)


class CandidateSkillCreate(CandidateSkillBase):
    pass


class CandidateSkill(CandidateSkillBase):
    id: UUID
    candidate_id: UUID

    class Config:
        from_attributes = True


class CandidateBase(BaseModel):
    display_name: str
    headline_role: str
    experience_years: Decimal = Field(..., ge=0, le=65)
    location: Optional[str] = None
    work_modes: List[str] = ["remote"]
    contacts: dict
    skills: List[CandidateSkillCreate] = []


class CandidateCreate(CandidateBase):
    telegram_id: int


class Candidate(CandidateBase):
    id: UUID
    telegram_id: int
    skills: List[CandidateSkill] = []
    resumes: List[Resume] = []

    class Config:
        from_attributes = True


class CandidateUpdate(BaseModel):
    display_name: Optional[str] = None
    headline_role: Optional[str] = None
    experience_years: Optional[Decimal] = Field(None, ge=0, le=65)
    location: Optional[str] = None
    work_modes: Optional[List[str]] = None
    contacts: Optional[dict] = None
    skills: Optional[List[CandidateSkillCreate]] = None

    class Config:
        from_attributes = True
