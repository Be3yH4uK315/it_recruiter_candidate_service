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
    Text,
    Date
)
from sqlalchemy.dialects.postgresql import UUID, BIGINT, JSONB, NUMERIC
from app.core.db import Base
import enum

# --- CONTACTS ---
class ContactsVisibility(str, enum.Enum):
    ON_REQUEST = "on_request"
    PUBLIC = "public"
    HIDDEN = "hidden"

# --- STATUS ---
class Status(str, enum.Enum):
    ACTIVE = "active"
    HIDDEN = "hidden"
    BLOCKED = "blocked"

# --- SKILLS ---
class SkillKind(str, enum.Enum):
    HARD = "hard"
    TOOL = "tool"
    LANGUAGE = "language"

class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    skill = Column(String(100), nullable=False)
    kind = Column(SQLAlchemyEnum(SkillKind), nullable=False)
    level = Column(SmallInteger, nullable=True)
    
    candidate = relationship("Candidate", back_populates="skills")

# --- RESUME ---
class Resume(Base):
    __tablename__ = "resumes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    file_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now())
    candidate = relationship("Candidate", back_populates="resumes")

# --- PROJECT ---
class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    links = Column(JSONB)

    candidate = relationship("Candidate", back_populates="projects")

# --- EXPERIENCE ---
class Experience(Base):
    __tablename__ = "experiences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id"), nullable=False)
    company = Column(String(255), nullable=False)
    position = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    responsibilities = Column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="experiences")

# --- CANDIDATE ---
class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telegram_id = Column(BIGINT, unique=True, index=True, nullable=False)
    display_name = Column(String(255))
    headline_role = Column(String(255))
    experience_years = Column(NUMERIC(3, 1))
    location = Column(String(255), nullable=True)
    work_modes = Column(JSONB)
    contacts_visibility = Column(SQLAlchemyEnum(ContactsVisibility), default=ContactsVisibility.ON_REQUEST, nullable=False)
    contacts = Column(JSONB)
    status = Column(SQLAlchemyEnum(Status), default=Status.ACTIVE, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan", lazy="joined")
    resumes = relationship("Resume", back_populates="candidate", cascade="all, delete-orphan", lazy="joined")
    projects = relationship("Project", back_populates="candidate", cascade="all, delete-orphan", lazy="joined")
    experiences = relationship("Experience", back_populates="candidate", cascade="all, delete-orphan", lazy="joined")
