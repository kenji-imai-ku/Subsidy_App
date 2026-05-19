from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories import program_repository


def get_programs(
    db: Session,
    category: str | None = None,
    support_type: str | None = None,
    prefecture: str | None = None,
    city: str | None = None,
    ward: str | None = None,
    application_required: bool | None = None,
    active_only: bool = True,
    keyword: str | None = None,
):
    return program_repository.list_programs(
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


def get_program_detail(db: Session, program_id: int):
    program = program_repository.get_program_by_id(db, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return program
