from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from app.models.candidate import SkillKind


class ResumeDownloadLink(BaseModel):
    download_url: str


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

    model_config = ConfigDict(from_attributes=True)


class CandidateSkillBase(BaseModel):
    skill: str
    kind: SkillKind
    level: Optional[int] = Field(None, ge=1, le=5)


class CandidateSkillCreate(CandidateSkillBase):
    pass


class CandidateSkill(CandidateSkillBase):
    id: UUID
    candidate_id: UUID

    model_config = ConfigDict(from_attributes=True)


class CandidateBase(BaseModel):
    display_name: str
    headline_role: str
    experience_years: Decimal = Field(..., ge=0, le=65)
    location: Optional[str] = None
    work_modes: List[str] = Field(default_factory=lambda: ["remote"])
    contacts: Dict[str, Any]
    skills: List[CandidateSkillCreate] = Field(default_factory=list)


class CandidateCreate(CandidateBase):
    telegram_id: int


class Candidate(CandidateBase):
    id: UUID
    telegram_id: int
    skills: List[CandidateSkill] = Field(default_factory=list)
    resumes: List[Resume] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class CandidateUpdate(BaseModel):
    display_name: Optional[str] = None
    headline_role: Optional[str] = None
    experience_years: Optional[Decimal] = Field(None, ge=0, le=65)
    location: Optional[str] = None
    work_modes: Optional[List[str]] = None
    contacts: Optional[Dict[str, Any]] = None
    skills: Optional[List[CandidateSkillCreate]] = None

    model_config = ConfigDict(from_attributes=True)