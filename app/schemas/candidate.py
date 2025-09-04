from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from decimal import Decimal

class CandidateBase(BaseModel):
    display_name: str
    headline_role: str
    experience_years: Decimal = Field(..., ge=0, le=65)
    location: Optional[str] = None
    work_modes: Optional[str] = "remote"
    contacts: dict


class CandidateCreate(CandidateBase):
    telegram_id: int


class Candidate(CandidateBase):
    id: UUID
    telegram_id: int

    class Config:
        from_attributes = True