import json
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
from app import crud, schemas
from app.core.db import get_db
from app.services.publisher import publisher, RabbitMQProducer

router = APIRouter()

# --- SUPPORT FUNCTION ---
async def get_publisher():
    return publisher

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

# --- CANDIDATE ---
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

# --- RESUME ---
@router.put("/by-telegram/{telegram_id}/resume", response_model=schemas.Resume)
def replace_candidate_resume(
    telegram_id: int,
    resume_in: schemas.ResumeCreate,
    db: Session = Depends(get_db)
):
    db_candidate = crud.get_candidate_by_telegram_id(db, telegram_id=telegram_id)
    if not db_candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    new_resume, old_file_id = crud.replace_resume(db=db, candidate=db_candidate, resume_in=resume_in)

    return new_resume

@router.delete("/by-telegram/{telegram_id}/resume", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate_resume(
    telegram_id: int,
    db: Session = Depends(get_db),
    pub: RabbitMQProducer = Depends(get_publisher)
):
    db_candidate = crud.get_candidate_by_telegram_id(db, telegram_id=telegram_id)
    if not db_candidate:
        raise HTTPException(status_code=404, detail="Кандидат не найден")
    db_resume = crud.delete_resume(db, candidate_id=db_candidate.id)
    if not db_resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")
    pydantic_candidate = schemas.Candidate.model_validate(db_candidate)
    await pub.publish_message(
        routing_key="candidate.updated",
        message_body=pydantic_candidate.model_dump_json().encode()
    )
    return None

# --- AVATAR ---
@router.put("/by-telegram/{telegram_id}/avatar", response_model=schemas.Avatar)
async def replace_candidate_avatar(
    telegram_id: int,
    avatar_in: schemas.AvatarCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    pub: RabbitMQProducer = Depends(get_publisher)
):
    db_candidate = crud.get_candidate_by_telegram_id(db, telegram_id=telegram_id)
    if not db_candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    new_avatar, old_file_id = crud.replace_avatar(db=db, candidate=db_candidate, avatar_in=avatar_in)

    if old_file_id:
        message_body = json.dumps({
            "file_id": str(old_file_id),
            "owner_telegram_id": telegram_id
        }).encode()
        background_tasks.add_task(
            pub.publish_message,
            routing_key="file.avatar.deleted",
            message_body=message_body
        )

    updated_candidate = crud.get_candidate(db, candidate_id=db_candidate.id)
    pydantic_candidate = schemas.Candidate.model_validate(updated_candidate)
    await pub.publish_message(
        routing_key="candidate.updated",
        message_body=pydantic_candidate.model_dump_json().encode()
    )

    return new_avatar

@router.delete("/by-telegram/{telegram_id}/avatar", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate_avatar(
    telegram_id: int,
    db: Session = Depends(get_db),
    pub: RabbitMQProducer = Depends(get_publisher)
):
    db_candidate = crud.get_candidate_by_telegram_id(db, telegram_id=telegram_id)
    if not db_candidate:
        raise HTTPException(status_code=404, detail="Кандидат не найден")
    db_avatar = crud.delete_avatar(db, candidate_id=db_candidate.id)
    if not db_avatar:
        raise HTTPException(status_code=404, detail="Аватарка не найдена")
    pydantic_candidate = schemas.Candidate.model_validate(db_candidate)
    await pub.publish_message(
        routing_key="candidate.updated",
        message_body=pydantic_candidate.model_dump_json().encode()
    )
    return None