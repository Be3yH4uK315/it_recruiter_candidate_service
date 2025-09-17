from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from app.models.candidate import SkillKind

# --- AVATAR ---
class AvatarBase(BaseModel):
    file_id: UUID

class AvatarCreate(AvatarBase):
    pass

class Avatar(AvatarBase):
    id: UUID
    candidate_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- PROJECT ---
class ProjectBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    links: Optional[Dict[str, Any]] = None

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: UUID
    candidate_id: UUID

    model_config = ConfigDict(from_attributes=True)

class ProjectUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    links: Optional[Dict[str, Any]] = None

# --- RESUME ---
class ResumeDownloadLink(BaseModel):
    download_url: str

class ResumeBase(BaseModel):
    file_id: UUID

class ResumeCreate(ResumeBase):
    pass

class Resume(ResumeBase):
    id: UUID
    candidate_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- SKILLS ---
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

# --- CANDIDATE ---
class CandidateBase(BaseModel):
    display_name: str
    headline_role: str
    experience_years: Decimal = Field(..., ge=0, le=65)
    location: Optional[str] = None
    work_modes: List[str] = Field(default_factory=lambda: ["remote"])
    contacts: Dict[str, Any]
    skills: List[CandidateSkillCreate] = Field(default_factory=list)
    projects: List[ProjectCreate] = Field(default_factory=list)

class CandidateCreate(CandidateBase):
    telegram_id: int

class Candidate(CandidateBase):
    id: UUID
    telegram_id: int
    skills: List[CandidateSkill] = Field(default_factory=list)
    resumes: List[Resume] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    avatars: List[Avatar] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class CandidateUpdate(BaseModel):
    display_name: Optional[str] = None
    headline_role: Optional[str] = None
    experience_years: Optional[Decimal] = Field(None, ge=0, le=65)
    location: Optional[str] = None
    work_modes: Optional[List[str]] = None
    contacts: Optional[Dict[str, Any]] = None
    skills: Optional[List[CandidateSkillCreate]] = None
    projects: Optional[List[ProjectCreate]] = None

    model_config = ConfigDict(from_attributes=True)