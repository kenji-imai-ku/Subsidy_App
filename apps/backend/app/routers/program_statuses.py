from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.user_program_status import UserProgramStatusRequest, UserProgramStatusResponse
from app.services import user_program_status_service

router = APIRouter(prefix="/program-statuses", tags=["program-statuses"])


@router.get("", response_model=List[UserProgramStatusResponse])
def read_user_program_statuses(db: Session = Depends(get_db)):
    return user_program_status_service.get_user_program_statuses(db)


@router.put("/{program_id}", response_model=UserProgramStatusResponse)
def update_user_program_status(
    program_id: int,
    request: UserProgramStatusRequest,
    db: Session = Depends(get_db)
):
    return user_program_status_service.upsert_user_program_status(db, program_id, request)
