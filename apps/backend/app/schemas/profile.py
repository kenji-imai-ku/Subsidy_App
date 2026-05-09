from datetime import date
from pydantic import BaseModel
from typing import Optional


class ProfileRequest(BaseModel):
    name: str
    prefecture: str
    birthYear: str
    birthMonth: str
    birthDay: str
    householdIncome: str
    familyType: str
    childrenCount: Optional[str] = "0"
    gender: str
    taxExempt: str


class ProfileResponse(BaseModel):
    id: int
    name: str
    prefecture: str
    birthDate: date
    gender: str
    householdIncome: str
    familyType: str
    childrenCount: int
    taxExempt: str

    class Config:
        from_attributes = True


class ProfileInternalData(BaseModel):
    name: str
    prefecture: str
    birth_date: date
    gender: str
    household_income_label: str
    annual_income_max: Optional[int]
    family_type: str
    has_spouse: Optional[bool]
    children_count: int
    has_children: bool
    is_single_parent: Optional[bool]
    is_tax_exempt_household: Optional[bool]
