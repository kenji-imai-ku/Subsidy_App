from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserProgramStatus(Base):
    __tablename__ = "user_program_statuses"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("support_programs.id"), nullable=False)

    status = Column(String, nullable=True)  # interested, checking, applied, approved, rejected, not_applicable
    is_favorite = Column(Boolean, nullable=False, default=False)
    memo = Column(Text, nullable=True)
    last_viewed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    profile = relationship("UserProfile", back_populates="program_statuses")
    program = relationship("SupportProgram")

    __table_args__ = (
        UniqueConstraint("profile_id", "program_id", name="uix_profile_program"),
    )
