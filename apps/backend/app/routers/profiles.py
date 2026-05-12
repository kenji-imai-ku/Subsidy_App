from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.profile import ProfileRequest, ProfileResponse
from app.services.profile_service import get_profile, upsert_profile, to_profile_response


router = APIRouter(prefix="/profile", tags=["profiles"])


@router.get("", response_model=ProfileResponse)
def read_profile(db: Session = Depends(get_db)):
    profile = get_profile(db)
    return to_profile_response(profile)


@router.put("", response_model=ProfileResponse)
def update_profile(request: ProfileRequest, db: Session = Depends(get_db)):
    profile = upsert_profile(db, request)
    return to_profile_response(profile)
