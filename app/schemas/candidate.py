from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from app.models.candidate import SkillKind


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
    work_modes: Optional[str] = "remote"
    contacts: dict
    skills: List[CandidateSkillCreate] = []


class CandidateCreate(CandidateBase):
    telegram_id: int


class Candidate(CandidateBase):
    id: UUID
    telegram_id: int
    skills: List[CandidateSkill] = []

    class Config:
        from_attributes = True


class CandidateUpdate(BaseModel):
    display_name: Optional[str] = None
    headline_role: Optional[str] = None
    experience_years: Optional[Decimal] = Field(None, ge=0, le=65)
    location: Optional[str] = None
    work_modes: Optional[str] = None
    contacts: Optional[dict] = None

    class Config:
        from_attributes = True