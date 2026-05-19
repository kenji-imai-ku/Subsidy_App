from sqlalchemy.orm import Session, joinedload
from app.models.support_program import SupportProgram


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

    if active_only:
        query = query.filter(SupportProgram.is_active == True)

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


def list_programs_with_conditions(db: Session):
    return (
        db.query(SupportProgram)
        .options(joinedload(SupportProgram.condition))
        .filter(SupportProgram.is_active == True)
        .order_by(SupportProgram.id.asc())
        .all()
    )
