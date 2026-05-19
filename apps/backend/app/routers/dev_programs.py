from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.support_program import ProgramCreateRequest, ProgramUpdateRequest, ProgramDetailResponse
from app.services import program_service


router = APIRouter(prefix="/dev/programs", tags=["dev"])


@router.post("", response_model=ProgramDetailResponse)
def create_program(request: ProgramCreateRequest, db: Session = Depends(get_db)):
    return program_service.create_program(db, request)


@router.put("/{program_id}", response_model=ProgramDetailResponse)
def update_program(program_id: int, request: ProgramUpdateRequest, db: Session = Depends(get_db)):
    return program_service.update_program(db, program_id, request)


@router.post("/seed", tags=["dev"])
def seed_programs(db: Session = Depends(get_db)):
    from app.seed.seed_programs import seed_programs_data
    return seed_programs_data(db)
