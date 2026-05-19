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

    # v2 Extension: Support Type and Amount
    support_type = Column(String, nullable=True)
    benefit_amount_type = Column(String, nullable=True)
    benefit_amount = Column(Integer, nullable=True)
    benefit_unit = Column(String, nullable=True)

    target_prefecture = Column(String, nullable=True)
    target_city = Column(String, nullable=True)
    target_ward = Column(String, nullable=True)

    # v2 Extension: Application Details
    application_required = Column(Boolean, nullable=True)
    application_method = Column(String, nullable=True)
    application_period_type = Column(String, nullable=True)
    application_url = Column(Text, nullable=True)
    deadline = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)

    required_documents = Column(Text, nullable=True)
    
    # v2 Extension: Contact and Source Details
    contact_department = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    
    source_url = Column(Text, nullable=True)
    source_updated_at = Column(Date, nullable=True)
    data_confirmed_at = Column(Date, nullable=True)
    confidence_level = Column(String, nullable=True)
    
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    condition = relationship(
        "SupportProgramCondition",
        back_populates="program",
        uselist=False,
        cascade="all, delete-orphan",
    )

    sources = relationship(
        "ProgramSource",
        back_populates="program",
        cascade="all, delete-orphan",
    )

    required_document_items = relationship(
        "ProgramRequiredDocument",
        back_populates="program",
        cascade="all, delete-orphan",
    )


class SupportProgramCondition(Base):
    __tablename__ = "support_program_conditions"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("support_programs.id"), nullable=False)

    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)

    max_annual_income = Column(Integer, nullable=True)
    
    # v2 Extension: More detailed income and asset conditions
    max_monthly_income = Column(Integer, nullable=True)
    max_savings_amount = Column(Integer, nullable=True)

    requires_tax_exempt = Column(Boolean, nullable=True)
    requires_children = Column(Boolean, nullable=True)
    min_children_count = Column(Integer, nullable=True)
    requires_single_parent = Column(Boolean, nullable=True)

    required_gender = Column(String, nullable=True)
    
    # v2 Extension: Regional and employment conditions
    required_city = Column(String, nullable=True)
    required_ward = Column(String, nullable=True)
    
    requires_unemployed = Column(Boolean, nullable=True)
    unemployed_within_months = Column(Integer, nullable=True)
    requires_job_seeking = Column(Boolean, nullable=True)
    requires_income_decreased = Column(Boolean, nullable=True)
    
    # v2 Extension: Health, Family and Housing conditions
    requires_health_insurance = Column(Boolean, nullable=True)
    requires_pregnancy = Column(Boolean, nullable=True)
    max_postpartum_months = Column(Integer, nullable=True)
    
    requires_disability = Column(Boolean, nullable=True)
    required_disability_type = Column(String, nullable=True)
    
    requires_medical_care_child = Column(Boolean, nullable=True)
    requires_young_carer = Column(Boolean, nullable=True)
    requires_household_head = Column(Boolean, nullable=True)
    requires_rent = Column(Boolean, nullable=True)

    condition_description = Column(Text, nullable=True)
    condition_text_original = Column(Text, nullable=True)
    manual_check_required = Column(Boolean, nullable=False, default=False)

    program = relationship("SupportProgram", back_populates="condition")
