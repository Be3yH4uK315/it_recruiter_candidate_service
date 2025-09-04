from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app import crud, schemas
from app.core.db import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Candidate, status_code=status.HTTP_201_CREATED)
def create_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(get_db)):
    db_candidate = crud.candidate.get_candidate_by_telegram_id(db, telegram_id=candidate.telegram_id)
    if db_candidate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Candidate with this Telegram ID already exists"
        )
    return crud.candidate.create_candidate(db=db, candidate=candidate)

@router.get("/{candidate_id}", response_model=schemas.Candidate)
def read_candidate(candidate_id: UUID, db: Session = Depends(get_db)):
    db_candidate = crud.candidate.get_candidate(db, candidate_id=candidate_id)
    if db_candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return db_candidate

@router.patch("/{candidate_id}", response_model=schemas.Candidate)
def update_candidate(
    candidate_id: UUID,
    candidate_in: schemas.CandidateUpdate,
    db: Session = Depends(get_db)
):
    db_candidate = crud.candidate.get_candidate(db, candidate_id=candidate_id)
    if db_candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )

    updated_candidate = crud.candidate.update_candidate(
        db=db,
        db_candidate=db_candidate,
        candidate_in=candidate_in
    )
    return updated_candidate