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


def create_program(db: Session, request: Any):
    # Mapping Pydantic to dict
    program_data = request.model_dump(exclude={"condition", "sources"})
    
    condition_data = None
    if request.condition:
        condition_data = request.condition.model_dump()
        
    sources_data = None
    if request.sources:
        sources_data = [s.model_dump() for s in request.sources]
        
    return program_repository.create_program(
        db, 
        program_data=program_data, 
        condition_data=condition_data, 
        sources_data=sources_data
    )


def update_program(db: Session, program_id: int, request: Any):
    # Mapping Pydantic to dict (only provided fields)
    program_data = request.model_dump(exclude={"condition", "sources"}, exclude_unset=True)
    
    condition_data = None
    if request.condition:
        condition_data = request.condition.model_dump(exclude_unset=True)
        
    sources_data = None
    if request.sources is not None:
        sources_data = [s.model_dump() for s in request.sources]
        
    program = program_repository.update_program(
        db,
        program_id=program_id,
        program_data=program_data,
        condition_data=condition_data,
        sources_data=sources_data
    )
    
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
        
    return program
