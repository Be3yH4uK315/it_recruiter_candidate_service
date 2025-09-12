import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app import crud, schemas
from app.core.db import get_db
from app.services.publisher import publisher, RabbitMQProducer
from app.services.file_service_client import file_service_client


router = APIRouter()


async def get_publisher():
    return publisher


@router.post("/", response_model=schemas.Candidate, status_code=status.HTTP_201_CREATED)
async def create_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(get_db), pub: RabbitMQProducer = Depends(get_publisher)):
    db_candidate = crud.candidate.get_candidate_by_telegram_id(
        db, telegram_id=candidate.telegram_id
    )
    if db_candidate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Candidate with this Telegram ID already exists",
        )
    db_candidate = crud.create_candidate(db=db, candidate=candidate)

    pydantic_candidate = schemas.Candidate.model_validate(db_candidate)
    await pub.publish_message(
        routing_key="candidate.created",
        message_body=pydantic_candidate.model_dump_json().encode()
    )

    return db_candidate


@router.get("/all", response_model=list[schemas.Candidate])
def get_all_candidates(db: Session = Depends(get_db)):
    return crud.candidate.get_all_candidates(db)


@router.get("/{candidate_id}", response_model=schemas.Candidate)
def read_candidate(candidate_id: UUID, db: Session = Depends(get_db)):
    db_candidate = crud.candidate.get_candidate(db, candidate_id=candidate_id)
    if db_candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )
    return db_candidate


async def handle_update(db_candidate, candidate_in, db, pub):
    updated_candidate = crud.update_candidate(
        db=db, db_candidate=db_candidate, candidate_in=candidate_in
    )
    pydantic_candidate = schemas.Candidate.model_validate(updated_candidate)
    await pub.publish_message(
        routing_key="candidate.updated",
        message_body=pydantic_candidate.model_dump_json().encode()
    )
    return updated_candidate


@router.patch("/{candidate_id}", response_model=schemas.Candidate)
async def update_candidate(
    candidate_id: UUID,
    candidate_in: schemas.CandidateUpdate,
    db: Session = Depends(get_db),
    pub: RabbitMQProducer = Depends(get_publisher)
):
    db_candidate = crud.get_candidate(db, candidate_id=candidate_id)
    if db_candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )
    return await handle_update(db_candidate, candidate_in, db, pub)


@router.patch("/by-telegram/{telegram_id}", response_model=schemas.Candidate)
async def update_candidate_by_telegram_id(
    telegram_id: int,
    candidate_in: schemas.CandidateUpdate,
    db: Session = Depends(get_db),
    pub: RabbitMQProducer = Depends(get_publisher)
):
    db_candidate = crud.get_candidate_by_telegram_id(
        db, telegram_id=telegram_id
    )
    if db_candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )
    return await handle_update(db_candidate, candidate_in, db, pub)


@router.post("/by-telegram/{telegram_id}/resume", response_model=schemas.Resume, status_code=status.HTTP_201_CREATED)
def add_resume_for_candidate(
    telegram_id: int,
    resume_in: schemas.ResumeCreate,
    db: Session = Depends(get_db)
):
    db_candidate = crud.get_candidate_by_telegram_id(db, telegram_id=telegram_id)
    if not db_candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    return crud.add_resume(db=db, candidate=db_candidate, resume_in=resume_in)

@router.get("/by-telegram/{telegram_id}", response_model=schemas.Candidate)
def read_candidate_by_telegram_id(
    telegram_id: int,
    db: Session = Depends(get_db),
):
    db_candidate = crud.candidate.get_candidate_by_telegram_id(db, telegram_id=telegram_id)
    if db_candidate is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )
    return db_candidate


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
        candidate_id: UUID,
        db: Session = Depends(get_db),
        pub: RabbitMQProducer = Depends(get_publisher)
):
    deleted_candidate = crud.delete_candidate(db, candidate_id=candidate_id)
    if not deleted_candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found"
        )

    message_body = json.dumps({"id": str(deleted_candidate.id)}).encode()
    await pub.publish_message(
        routing_key="candidate.deleted",
        message_body=message_body
    )

    return None


@router.get("/{candidate_id}/resume", response_model=schemas.ResumeDownloadLink)
async def get_resume_download_link(candidate_id: UUID, db: Session = Depends(get_db)):
    db_candidate = crud.get_candidate(db, candidate_id=candidate_id)

    if not db_candidate or not db_candidate.resumes:
        raise HTTPException(status_code=404, detail="Resume not found for this candidate")

    latest_resume = db_candidate.resumes[-1]
    object_key = latest_resume.object_key

    download_url = await file_service_client.get_download_url(object_key)

    if not download_url:
        raise HTTPException(status_code=503, detail="File Storage Service is unavailable")

    return {"download_url": download_url}