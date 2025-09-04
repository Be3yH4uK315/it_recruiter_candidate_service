import uuid
from sqlalchemy import Column, String, Text, Enum as SQLAlchemyEnum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, BIGINT, JSONB, NUMERIC
from app.core.db import Base
import enum

class ContactsVisibility(str, enum.Enum):
    ON_REQUEST = "on_request"
    PUBLIC = "public"
    HIDDEN = "hidden"

class Status(str, enum.Enum):
    ACTIVE = "active"
    HIDDEN = "hidden"
    BLOCKED = "blocked"


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
        nullable=False
    )
    contacts = Column(JSONB)

    status = Column(
        SQLAlchemyEnum(Status),
        default=Status.ACTIVE,
        nullable=False
    )

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())