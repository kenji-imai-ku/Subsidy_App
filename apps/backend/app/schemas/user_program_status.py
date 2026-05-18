from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class UserProgramStatusRequest(BaseModel):
    status: Optional[str] = None
    isFavorite: bool = False
    memo: Optional[str] = None


class UserProgramStatusResponse(BaseModel):
    programId: int = Field(..., validation_alias="program_id", serialization_alias="programId")
    status: Optional[str] = None
    isFavorite: bool = Field(..., validation_alias="is_favorite", serialization_alias="isFavorite")
    memo: Optional[str] = None
    lastViewedAt: Optional[datetime] = Field(None, validation_alias="last_viewed_at", serialization_alias="lastViewedAt")
    updatedAt: Optional[datetime] = Field(None, validation_alias="updated_at", serialization_alias="updatedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
