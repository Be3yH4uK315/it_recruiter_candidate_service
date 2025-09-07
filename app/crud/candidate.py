from sqlalchemy.orm import Session
from uuid import UUID
from app import models, schemas


def get_candidate_by_telegram_id(db: Session, telegram_id: int):
    return (
        db.query(models.Candidate)
        .filter(models.Candidate.telegram_id == telegram_id)
        .first()
    )


def create_candidate(db: Session, candidate: schemas.CandidateCreate):
    skills_data = candidate.skills
    candidate_data = candidate.model_dump(exclude={"skills"})

    db_candidate = models.Candidate(**candidate_data)

    for skill_in in skills_data:
        db_skill = models.CandidateSkill(
            **skill_in.model_dump(), candidate=db_candidate
        )
        db.add(db_skill)

    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


def get_candidate(db: Session, candidate_id: UUID):
    return (
        db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    )


def get_all_candidates(db: Session):
    return db.query(models.Candidate).all()


def update_candidate(
    db: Session, db_candidate: models.Candidate, candidate_in: schemas.CandidateUpdate
):
    update_data = candidate_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field != "skills":
            setattr(db_candidate, field, value)

    if "skills" in update_data and update_data["skills"] is not None:
        db.query(models.CandidateSkill).filter(
            models.CandidateSkill.candidate_id == db_candidate.id
        ).delete(synchronize_session=False)

        for skill_in in candidate_in.skills:
            db_skill = models.CandidateSkill(
                **skill_in.model_dump(), candidate_id=db_candidate.id
            )
            db.add(db_skill)

    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate


def add_resume(db: Session, candidate: models.Candidate, resume_in: schemas.ResumeCreate) -> models.Resume:
    db_resume = models.Resume(**resume_in.model_dump(), candidate_id=candidate.id)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume


def delete_candidate(db: Session, candidate_id: UUID) -> models.Candidate | None:
    db_candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if db_candidate:
        db.delete(db_candidate)
        db.commit()
    return db_candidate