from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SupportProgram(Base):
    __tablename__ = "support_programs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    benefit = Column(Text, nullable=True)
    category = Column(String, nullable=True)

    target_prefecture = Column(String, nullable=True)
    target_city = Column(String, nullable=True)
    target_ward = Column(String, nullable=True)

    application_url = Column(Text, nullable=True)
    deadline = Column(Date, nullable=True)
    required_documents = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    condition = relationship(
        "SupportProgramCondition",
        back_populates="program",
        uselist=False,
        cascade="all, delete-orphan",
    )


class SupportProgramCondition(Base):
    __tablename__ = "support_program_conditions"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("support_programs.id"), nullable=False)

    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)

    max_annual_income = Column(Integer, nullable=True)

    requires_tax_exempt = Column(Boolean, nullable=True)
    requires_children = Column(Boolean, nullable=True)
    min_children_count = Column(Integer, nullable=True)
    requires_single_parent = Column(Boolean, nullable=True)

    required_gender = Column(String, nullable=True)

    condition_description = Column(Text, nullable=True)

    program = relationship("SupportProgram", back_populates="condition")
