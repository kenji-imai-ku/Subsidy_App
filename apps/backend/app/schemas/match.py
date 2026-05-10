from pydantic import BaseModel
from typing import List
from app.schemas.support_program import ProgramListItemResponse


class MatchResultResponse(BaseModel):
    program: ProgramListItemResponse
    score: int
    status: str
    reasons: List[str]
    warnings: List[str]
