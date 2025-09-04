from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
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