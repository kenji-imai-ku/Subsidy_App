from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.user_program_status import UserProgramStatusRequest
from app.repositories import user_program_status_repository, profile_repository, program_repository


def get_user_program_statuses(db: Session):
    profile = profile_repository.get_current_profile(db)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    statuses = user_program_status_repository.get_user_program_statuses(db, profile.id)
    return statuses


def upsert_user_program_status(db: Session, program_id: int, request: UserProgramStatusRequest):
    profile = profile_repository.get_current_profile(db)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    program = program_repository.get_program_by_id(db, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    data = request.model_dump(exclude_unset=True)
    # 既存フィールドのマッピング (camelCase -> snake_case)
    if "isFavorite" in data:
        data["is_favorite"] = data.pop("isFavorite")
    
    data["last_viewed_at"] = datetime.now(timezone.utc)

    status_record = user_program_status_repository.upsert_user_program_status(
        db, profile.id, program_id, data
    )
    return status_record
