from datetime import date

from sqlalchemy.orm import Session
from uuid import UUID
from app import models, schemas

# --- CANDIDATE ---
def get_candidate_by_telegram_id(db: Session, telegram_id: int):
    return (
        db.query(models.Candidate)
        .filter(models.Candidate.telegram_id == telegram_id)
        .first()
    )

def get_candidate(db: Session, candidate_id: UUID):
    return (
        db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    )

def get_all_candidates(db: Session):
    return db.query(models.Candidate).all()

def create_candidate(db: Session, candidate: schemas.CandidateCreate):
    skills_data = candidate.skills
    projects_data = candidate.projects
    candidate_data = candidate.model_dump(exclude={"skills", "projects"})

    db_candidate = models.Candidate(**candidate_data)

    for skill_in in skills_data:
        db_skill = models.CandidateSkill(
            **skill_in.model_dump(), candidate=db_candidate
        )
        db.add(db_skill)

    for project_in in projects_data:
        db_project = models.Project(
            **project_in.model_dump(), candidate=db_candidate
        )
        db.add(db_project)

    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

def update_candidate(
    db: Session, db_candidate: models.Candidate, candidate_in: schemas.CandidateUpdate
):
    update_data = candidate_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if field not in ["skills", "projects", "experiences"]:
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

    if "projects" in update_data and update_data["projects"] is not None:
        db.query(models.Project).filter(
            models.Project.candidate_id == db_candidate.id
        ).delete(synchronize_session=False)

        for project_in in candidate_in.projects:
            db_project = models.Project(
                **project_in.model_dump(), candidate_id=db_candidate.id
            )
            db.add(db_project)

    if "experiences" in update_data and update_data["experiences"] is not None:
        db.query(models.Experience).filter(
            models.Experience.candidate_id == db_candidate.id
        ).delete(synchronize_session=False)

        new_experiences_models = []
        for exp_in in candidate_in.experiences:
            db_exp = models.Experience(
                **exp_in.model_dump(), candidate_id=db_candidate.id
            )
            db.add(db_exp)
            new_experiences_models.append(db_exp)

        total_exp_years = _calculate_total_experience(new_experiences_models)
        setattr(db_candidate, 'experience_years', total_exp_years)

    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

def delete_candidate(db: Session, candidate_id: UUID) -> models.Candidate | None:
    db_candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if db_candidate:
        db.delete(db_candidate)
        db.commit()
    return db_candidate

# --- RESUME ---
def add_resume(db: Session, candidate: models.Candidate, resume_in: schemas.ResumeCreate) -> models.Resume:
    db.query(models.Resume).filter(models.Resume.candidate_id == candidate.id).delete()
    db_resume = models.Resume(candidate_id=candidate.id, file_id=resume_in.file_id)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def replace_resume(db: Session, candidate: models.Candidate, resume_in: schemas.ResumeCreate) -> (models.Resume, UUID | None):
    old_file_id = None
    if candidate.resumes:
        old_resume_record = candidate.resumes[0]
        old_file_id = old_resume_record.file_id
        db.delete(old_resume_record)
        db.flush()

    new_resume_record = models.Resume(candidate_id=candidate.id, file_id=resume_in.file_id)
    db.add(new_resume_record)
    db.commit()
    db.refresh(new_resume_record)

    return new_resume_record, old_file_id

def delete_resume(db: Session, candidate_id: UUID) -> models.Resume | None:
    db_resume = db.query(models.Resume).filter(models.Resume.candidate_id == candidate_id).first()
    if db_resume:
        db.delete(db_resume)
        db.commit()
    return db_resume

# --- PROJECT ---
def add_project(db: Session, candidate: models.Candidate, project_in: schemas.ProjectCreate) -> models.Project:
    db_project = models.Project(**project_in.model_dump(), candidate_id=candidate.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: UUID) -> models.Project | None:
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if db_project:
        db.delete(db_project)
        db.commit()
    return db_project

# --- AVATAR ---
def replace_avatar(db: Session, candidate: models.Candidate, avatar_in: schemas.AvatarCreate) -> (models.Avatar, UUID | None):
    old_file_id = None
    if candidate.avatars:
        old_avatar_record = candidate.avatars[0]
        old_file_id = old_avatar_record.file_id
        db.delete(old_avatar_record)
        db.flush()

    new_avatar_record = models.Avatar(candidate_id=candidate.id, file_id=avatar_in.file_id)
    db.add(new_avatar_record)
    db.commit()
    db.refresh(new_avatar_record)

    return new_avatar_record, old_file_id

def delete_avatar(db:Session, candidate_id: UUID) -> models.Avatar | None:
    db_avatar = db.query(models.Avatar).filter(models.Avatar.candidate_id == candidate_id).first()
    if db_avatar:
        db.delete(db_avatar)
        db.commit()
    return db_avatar

# --- EXPERIENCE ---
def _calculate_total_experience(experiences: list[models.Experience]) -> float:
    if not experiences:
        return 0.0

    total_days = 0
    for exp in experiences:
        end_date = exp.end_date if exp.end_date else date.today()
        if end_date > exp.start_date:
            total_days += (end_date - exp.start_date).days

    return round(total_days / 365.25, 1)