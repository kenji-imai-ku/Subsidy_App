from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.support_program import ProgramListItemResponse, ProgramDetailResponse
from app.services.program_service import get_programs, get_program_detail


router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("", response_model=List[ProgramListItemResponse])
def read_programs(
    category: str | None = Query(default=None),
    support_type: str | None = Query(default=None, alias="supportType"),
    prefecture: str | None = Query(default=None),
    city: str | None = Query(default=None),
    ward: str | None = Query(default=None),
    application_required: bool | None = Query(default=None, alias="applicationRequired"),
    active_only: bool = Query(default=True, alias="activeOnly"),
    keyword: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return get_programs(
        db,
        category=category,
        support_type=support_type,
        prefecture=prefecture,
        city=city,
        ward=ward,
        application_required=application_required,
        active_only=active_only,
        keyword=keyword,
    )


@router.get("/{program_id}", response_model=ProgramDetailResponse)
def read_program_detail(program_id: int, db: Session = Depends(get_db)):
    return get_program_detail(db, program_id)
