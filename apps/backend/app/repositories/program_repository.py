from sqlalchemy.orm import Session, joinedload
from app.models.support_program import SupportProgram
from datetime import date


def list_programs(
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
    query = db.query(SupportProgram)
    today = date.today()

    if active_only:
        query = query.filter(SupportProgram.is_active == True)
        # 締切日または終了日が今日以前のものを除外
        query = query.filter(
            (SupportProgram.deadline == None) | (SupportProgram.deadline >= today)
        )
        query = query.filter(
            (SupportProgram.end_date == None) | (SupportProgram.end_date >= today)
        )

    if category:
        query = query.filter(SupportProgram.category == category)

    if support_type:
        query = query.filter(SupportProgram.support_type == support_type)

    if prefecture:
        query = query.filter(
            (SupportProgram.target_prefecture == prefecture)
            | (SupportProgram.target_prefecture == None)
        )

    if city:
        query = query.filter(
            (SupportProgram.target_city == city) | (SupportProgram.target_city == None)
        )

    if ward:
        query = query.filter(
            (SupportProgram.target_ward == ward) | (SupportProgram.target_ward == None)
        )

    if application_required is not None:
        query = query.filter(SupportProgram.application_required == application_required)

    if keyword:
        search_filter = (
            SupportProgram.title.ilike(f"%{keyword}%")
            | SupportProgram.summary.ilike(f"%{keyword}%")
            | SupportProgram.benefit.ilike(f"%{keyword}%")
            | SupportProgram.provider.ilike(f"%{keyword}%")
        )
        query = query.filter(search_filter)

    return query.order_by(SupportProgram.id.asc()).all()


def get_program_by_id(db: Session, program_id: int):
    return (
        db.query(SupportProgram)
        .options(
            joinedload(SupportProgram.condition),
            joinedload(SupportProgram.sources),
            joinedload(SupportProgram.required_document_items),
        )
        .filter(SupportProgram.id == program_id)
        .filter(SupportProgram.is_active == True)
        .first()
    )


def create_program(db: Session, program_data: dict, condition_data: dict | None = None, sources_data: list[dict] | None = None):
    from app.models.support_program import SupportProgramCondition
    from app.models.program_source import ProgramSource

    db_program = SupportProgram(**program_data)
    
    if condition_data:
        db_program.condition = SupportProgramCondition(**condition_data)
        
    if sources_data:
        for source in sources_data:
            db_program.sources.append(ProgramSource(**source))
            
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program


def update_program(
    db: Session,
    program_id: int,
    program_data: dict,
    condition_data: dict | None = None,
    sources_data: list[dict] | None = None,
):
    from app.models.support_program import SupportProgramCondition
    from app.models.program_source import ProgramSource

    db_program = (
        db.query(SupportProgram)
        .options(joinedload(SupportProgram.condition), joinedload(SupportProgram.sources))
        .filter(SupportProgram.id == program_id)
        .first()
    )
    
    if not db_program:
        return None

    # Update Program本体
    for key, value in program_data.items():
        setattr(db_program, key, value)

    # Update Condition
    if condition_data:
        if db_program.condition:
            for key, value in condition_data.items():
                setattr(db_program.condition, key, value)
        else:
            db_program.condition = SupportProgramCondition(**condition_data)

    # Update Sources (For simplicity in dev API, we replace all sources if provided)
    if sources_data is not None:
        db.query(ProgramSource).filter(ProgramSource.program_id == program_id).delete()
        for source in sources_data:
            db_program.sources.append(ProgramSource(**source))

    db.commit()
    db.refresh(db_program)
    return db_program


def list_programs_with_conditions(db: Session):
    today = date.today()
    return (
        db.query(SupportProgram)
        .options(joinedload(SupportProgram.condition))
        .filter(SupportProgram.is_active == True)
        .filter((SupportProgram.deadline == None) | (SupportProgram.deadline >= today))
        .filter((SupportProgram.end_date == None) | (SupportProgram.end_date >= today))
        .order_by(SupportProgram.id.asc())
        .all()
    )
