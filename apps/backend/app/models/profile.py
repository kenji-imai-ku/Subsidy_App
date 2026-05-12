from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    prefecture = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)

    gender = Column(String, nullable=False)

    household_income_label = Column(String, nullable=False)
    annual_income_max = Column(Integer, nullable=True)

    family_type = Column(String, nullable=False)
    has_spouse = Column(Boolean, nullable=True)

    children_count = Column(Integer, nullable=False, default=0)
    has_children = Column(Boolean, nullable=False, default=False)
    is_single_parent = Column(Boolean, nullable=True)

    is_tax_exempt_household = Column(Boolean, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
