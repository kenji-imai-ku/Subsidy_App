from sqlalchemy.orm import Session, joinedload
from app.models.support_program import SupportProgram


def list_programs(db: Session, category: str | None = None, prefecture: str | None = None):
    query = db.query(SupportProgram).filter(SupportProgram.is_active == True)

    if category:
        query = query.filter(SupportProgram.category == category)

    if prefecture:
        query = query.filter(
            (SupportProgram.target_prefecture == prefecture)
            | (SupportProgram.target_prefecture == None)
        )

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


def list_programs_with_conditions(db: Session):
    return (
        db.query(SupportProgram)
        .options(joinedload(SupportProgram.condition))
        .filter(SupportProgram.is_active == True)
        .order_by(SupportProgram.id.asc())
        .all()
    )
