from sqlalchemy.orm import Session
from app import models, schemas


def get_candidate_by_telegram_id(db: Session, telegram_id: int):
    return db.query(models.Candidate).filter(models.Candidate.telegram_id == telegram_id).first()


def create_candidate(db: Session, candidate: schemas.CandidateCreate):
    db_candidate_data = candidate.model_dump()

    db_candidate = models.Candidate(**db_candidate_data)

    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate