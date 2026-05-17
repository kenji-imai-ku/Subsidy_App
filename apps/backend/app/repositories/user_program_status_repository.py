from sqlalchemy.orm import Session
from app.models.user_program_status import UserProgramStatus


def get_user_program_statuses(db: Session, profile_id: int):
    return db.query(UserProgramStatus).filter(UserProgramStatus.profile_id == profile_id).all()


def get_user_program_status(db: Session, profile_id: int, program_id: int):
    return db.query(UserProgramStatus).filter(
        UserProgramStatus.profile_id == profile_id,
        UserProgramStatus.program_id == program_id
    ).first()


def upsert_user_program_status(db: Session, profile_id: int, program_id: int, data: dict):
    status_record = get_user_program_status(db, profile_id, program_id)
    
    if status_record:
        for key, value in data.items():
            setattr(status_record, key, value)
        db.commit()
        db.refresh(status_record)
        return status_record
    else:
        status_record = UserProgramStatus(
            profile_id=profile_id,
            program_id=program_id,
            **data
        )
        db.add(status_record)
        db.commit()
        db.refresh(status_record)
        return status_record
