from sqlalchemy.orm import Session
from app.models.profile import UserProfile


def get_current_profile(db: Session) -> UserProfile | None:
    return db.query(UserProfile).order_by(UserProfile.id.desc()).first()


def create_profile(db: Session, data: dict) -> UserProfile:
    profile = UserProfile(**data)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(db: Session, profile: UserProfile, data: dict) -> UserProfile:
    for key, value in data.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile
