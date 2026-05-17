from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class UserProgramStatusRequest(BaseModel):
    status: Optional[str] = None
    isFavorite: bool = False
    memo: Optional[str] = None


class UserProgramStatusResponse(BaseModel):
    programId: int = Field(..., alias="programId")
    status: Optional[str] = None
    isFavorite: bool = Field(..., alias="isFavorite")
    memo: Optional[str] = None
    lastViewedAt: Optional[datetime] = Field(None, alias="lastViewedAt")
    updatedAt: Optional[datetime] = Field(None, alias="updatedAt")

    class Config:
        from_attributes = True
        populate_by_name = True
