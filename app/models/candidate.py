import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    String,
    Enum as SQLAlchemyEnum,
    DateTime,
    func,
    ForeignKey,
    SmallInteger,
)
from sqlalchemy.dialects.postgresql import UUID, BIGINT, JSONB, NUMERIC
from app.core.db import Base
import enum


class SkillKind(str, enum.Enum):
    HARD = "hard"
    TOOL = "tool"
    LANGUAGE = "language"


class ContactsVisibility(str, enum.Enum):
    ON_REQUEST = "on_request"
    PUBLIC = "public"
    HIDDEN = "hidden"


class Status(str, enum.Enum):
    ACTIVE = "active"
    HIDDEN = "hidden"
    BLOCKED = "blocked"


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(
        UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False
    )
    skill = Column(String(100), nullable=False)
    kind = Column(SQLAlchemyEnum(SkillKind), nullable=False)
    level = Column(SmallInteger, nullable=True)

    candidate = relationship("Candidate", back_populates="skills")


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BIGINT, unique=True, index=True, nullable=False)
    display_name = Column(String(255))
    headline_role = Column(String(255))
    experience_years = Column(NUMERIC(3, 1))

    location = Column(String(255), nullable=True)
    work_modes = Column(String, default="remote")

    contacts_visibility = Column(
        SQLAlchemyEnum(ContactsVisibility),
        default=ContactsVisibility.ON_REQUEST,
        nullable=False,
    )
    contacts = Column(JSONB)

    status = Column(SQLAlchemyEnum(Status), default=Status.ACTIVE, nullable=False)

    skills = relationship(
        "CandidateSkill", back_populates="candidate", cascade="all, delete-orphan"
    )

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
