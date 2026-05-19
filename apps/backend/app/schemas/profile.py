from datetime import date
from pydantic import BaseModel, Field
from typing import Optional


class EmploymentStatusSchema(BaseModel):
    employmentStatus: Optional[str] = None
    isUnemployed: Optional[bool] = None
    unemployedSince: Optional[date] = None
    isJobSeeking: Optional[bool] = None
    incomeDecreased: Optional[bool] = None
    incomeDecreasedReason: Optional[str] = None

    class Config:
        from_attributes = True


class SpecialConditionSchema(BaseModel):
    hasHealthInsurance: Optional[bool] = None
    isPregnant: Optional[bool] = None
    postpartumMonths: Optional[int] = None
    hasDisability: Optional[bool] = None
    disabilityType: Optional[str] = None
    disabilityGrade: Optional[str] = None
    hasMedicalCareChild: Optional[bool] = None
    hasCareRequiredFamily: Optional[bool] = None
    hasYoungCarerInHousehold: Optional[bool] = None

    class Config:
        from_attributes = True


class ProfileRequest(BaseModel):
    name: str
    prefecture: str
    city: Optional[str] = None
    ward: Optional[str] = None
    birthYear: str
    birthMonth: str
    birthDay: str
    householdIncome: str
    monthlyIncome: Optional[int] = None
    savingsAmountRange: Optional[str] = None
    housingStatus: Optional[str] = None
    familyType: str
    hasSpouse: Optional[bool] = None
    childrenCount: Optional[str] = "0"
    gender: str
    taxExempt: str
    isHouseholdHead: Optional[bool] = None
    employment: Optional[EmploymentStatusSchema] = None
    specialConditions: Optional[SpecialConditionSchema] = None


class ProfileResponse(BaseModel):
    id: int
    name: str
    prefecture: str
    city: Optional[str] = None
    ward: Optional[str] = None
    birthDate: date = Field(..., alias="birthDate")
    gender: str
    householdIncome: str = Field(..., alias="householdIncome")
    annualIncomeMax: Optional[int] = Field(None, alias="annualIncomeMax")
    monthlyIncome: Optional[int] = Field(None, alias="monthlyIncome")
    savingsAmountRange: Optional[str] = Field(None, alias="savingsAmountRange")
    housingStatus: Optional[str] = Field(None, alias="housingStatus")
    familyType: str = Field(..., alias="familyType")
    hasSpouse: Optional[bool] = Field(None, alias="hasSpouse")
    childrenCount: int = Field(..., alias="childrenCount")
    hasChildren: bool = Field(..., alias="hasChildren")
    isSingleParent: Optional[bool] = Field(None, alias="isSingleParent")
    isTaxExemptHousehold: Optional[bool] = Field(None, alias="isTaxExemptHousehold")
    isHouseholdHead: Optional[bool] = Field(None, alias="isHouseholdHead")
    employment: Optional[EmploymentStatusSchema] = None
    specialConditions: Optional[SpecialConditionSchema] = None

    class Config:
        from_attributes = True
        populate_by_name = True


class ProfileInternalData(BaseModel):
    name: str
    prefecture: str
    city: Optional[str] = None
    ward: Optional[str] = None
    birth_date: date
    gender: str
    household_income_label: str
    annual_income_max: Optional[int]
    monthly_income: Optional[int] = None
    savings_amount_range: Optional[str] = None
    housing_status: Optional[str] = None
    family_type: str
    has_spouse: Optional[bool] = None
    children_count: int
    has_children: bool
    is_single_parent: Optional[bool] = None
    is_tax_exempt_household: Optional[bool] = None
    is_household_head: Optional[bool] = None
