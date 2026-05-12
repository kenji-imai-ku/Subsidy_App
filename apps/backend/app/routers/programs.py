from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.program_service import get_programs, get_program_detail


router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("")
def read_programs(
    category: str | None = Query(default=None),
    prefecture: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return get_programs(db, category=category, prefecture=prefecture)


@router.get("/{program_id}")
def read_program_detail(program_id: int, db: Session = Depends(get_db)):
    return get_program_detail(db, program_id)
