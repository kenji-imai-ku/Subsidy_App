from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories import program_repository


def get_programs(db: Session, category: str | None = None, prefecture: str | None = None):
    return program_repository.list_programs(
        db,
        category=category,
        prefecture=prefecture,
    )


def get_program_detail(db: Session, program_id: int):
    program = program_repository.get_program_by_id(db, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return program
