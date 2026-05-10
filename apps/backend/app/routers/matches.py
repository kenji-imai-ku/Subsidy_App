from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.match import MatchResultResponse
from app.services.matching_service import get_matches


router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=List[MatchResultResponse])
def read_matches(db: Session = Depends(get_db)):
    return get_matches(db)
