from sqlalchemy.orm import Session
from app.models.profile import UserProfile, ProfileEmploymentStatus, ProfileSpecialCondition


def get_current_profile(db: Session) -> UserProfile | None:
    return db.query(UserProfile).order_by(UserProfile.id.desc()).first()


def create_profile(db: Session, data: dict) -> UserProfile:
    employment_data = data.pop("employment", None)
    special_conditions_data = data.pop("special_conditions", None)

    profile = UserProfile(**data)
    
    if employment_data:
        profile.employment = ProfileEmploymentStatus(**employment_data)
    if special_conditions_data:
        profile.special_conditions = ProfileSpecialCondition(**special_conditions_data)
        
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(db: Session, profile: UserProfile, data: dict) -> UserProfile:
    employment_data = data.pop("employment", None)
    special_conditions_data = data.pop("special_conditions", None)

    for key, value in data.items():
        setattr(profile, key, value)
    
    if employment_data:
        if profile.employment:
            for key, value in employment_data.items():
                setattr(profile.employment, key, value)
        else:
            profile.employment = ProfileEmploymentStatus(**employment_data)
            
    if special_conditions_data:
        if profile.special_conditions:
            for key, value in special_conditions_data.items():
                setattr(profile.special_conditions, key, value)
        else:
            profile.special_conditions = ProfileSpecialCondition(**special_conditions_data)

    db.commit()
    db.refresh(profile)
    return profile
