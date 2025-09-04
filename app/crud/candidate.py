from sqlalchemy.orm import Session
from uuid import UUID
from app import models, schemas


def get_candidate_by_telegram_id(db: Session, telegram_id: int):
    return db.query(models.Candidate).filter(models.Candidate.telegram_id == telegram_id).first()


def create_candidate(db: Session, candidate: schemas.CandidateCreate):
    skills_data = candidate.skills
    candidate_data = candidate.model_dump(exclude={"skills"})

    db_candidate = models.Candidate(**candidate_data)

    for skill_in in skills_data:
        db_skill = models.CandidateSkill(**skill_in.model_dump(), candidate=db_candidate)
        db.add(db_skill)

    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


def get_candidate(db: Session, candidate_id: UUID):
    return db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()


def update_candidate(db: Session, db_candidate: models.Candidate, candidate_in: schemas.CandidateUpdate):
    update_data = candidate_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_candidate, field, value)

    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate