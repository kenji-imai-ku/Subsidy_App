from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    prefecture = Column(String, nullable=False)
    city = Column(String, nullable=True)
    ward = Column(String, nullable=True)
    birth_date = Column(Date, nullable=False)

    gender = Column(String, nullable=False)

    household_income_label = Column(String, nullable=False)
    annual_income_max = Column(Integer, nullable=True)
    monthly_income = Column(Integer, nullable=True)
    savings_amount_range = Column(String, nullable=True)
    housing_status = Column(String, nullable=True)

    family_type = Column(String, nullable=False)
    has_spouse = Column(Boolean, nullable=True)

    children_count = Column(Integer, nullable=False, default=0)
    has_children = Column(Boolean, nullable=False, default=False)
    is_single_parent = Column(Boolean, nullable=True)

    is_tax_exempt_household = Column(Boolean, nullable=True)
    is_household_head = Column(Boolean, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    employment = relationship(
        "ProfileEmploymentStatus", back_populates="profile", uselist=False, cascade="all, delete-orphan"
    )
    special_conditions = relationship(
        "ProfileSpecialCondition", back_populates="profile", uselist=False, cascade="all, delete-orphan"
    )
    program_statuses = relationship(
        "UserProgramStatus", back_populates="profile", cascade="all, delete-orphan"
    )


class ProfileEmploymentStatus(Base):
    __tablename__ = "profile_employment_statuses"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, unique=True)

    employment_status = Column(String, nullable=True)
    is_unemployed = Column(Boolean, nullable=True)
    unemployed_since = Column(Date, nullable=True)
    is_job_seeking = Column(Boolean, nullable=True)
    income_decreased = Column(Boolean, nullable=True)
    income_decreased_reason = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    profile = relationship("UserProfile", back_populates="employment")


class ProfileSpecialCondition(Base):
    __tablename__ = "profile_special_conditions"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("user_profiles.id"), nullable=False, unique=True)

    has_health_insurance = Column(Boolean, nullable=True)
    is_pregnant = Column(Boolean, nullable=True)
    postpartum_months = Column(Integer, nullable=True)
    has_disability = Column(Boolean, nullable=True)
    disability_type = Column(String, nullable=True)
    disability_grade = Column(String, nullable=True)
    has_medical_care_child = Column(Boolean, nullable=True)
    has_care_required_family = Column(Boolean, nullable=True)
    has_young_carer_in_household = Column(Boolean, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    profile = relationship("UserProfile", back_populates="special_conditions")
