from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field, AliasChoices
from typing import Optional, Any, List


class ProgramConditionResponse(BaseModel):
    minAge: Optional[int] = Field(None, validation_alias=AliasChoices("min_age", "minAge"))
    maxAge: Optional[int] = Field(None, validation_alias=AliasChoices("max_age", "maxAge"))
    maxAnnualIncome: Optional[int] = Field(None, validation_alias=AliasChoices("max_annual_income", "maxAnnualIncome"))
    maxMonthlyIncome: Optional[int] = Field(None, validation_alias=AliasChoices("max_monthly_income", "maxMonthlyIncome"))
    maxSavingsAmount: Optional[int] = Field(None, validation_alias=AliasChoices("max_savings_amount", "maxSavingsAmount"))
    
    requiresTaxExempt: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_tax_exempt", "requiresTaxExempt"))
    requiresChildren: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_children", "requiresChildren"))
    minChildrenCount: Optional[int] = Field(None, validation_alias=AliasChoices("min_children_count", "minChildrenCount"))
    requiresSingleParent: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_single_parent", "requiresSingleParent"))
    
    requiredGender: Optional[str] = Field(None, validation_alias=AliasChoices("required_gender", "requiredGender"))
    requiredCity: Optional[str] = Field(None, validation_alias=AliasChoices("required_city", "requiredCity"))
    requiredWard: Optional[str] = Field(None, validation_alias=AliasChoices("required_ward", "requiredWard"))
    
    requiresUnemployed: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_unemployed", "requiresUnemployed"))
    unemployedWithinMonths: Optional[int] = Field(None, validation_alias=AliasChoices("unemployed_within_months", "unemployedWithinMonths"))
    requiresJobSeeking: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_job_seeking", "requiresJobSeeking"))
    requiresIncomeDecreased: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_income_decreased", "requiresIncomeDecreased"))
    
    requiresHealthInsurance: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_health_insurance", "requiresHealthInsurance"))
    requiresPregnancy: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_pregnancy", "requiresPregnancy"))
    maxPostpartumMonths: Optional[int] = Field(None, validation_alias=AliasChoices("max_postpartum_months", "maxPostpartumMonths"))
    
    requiresDisability: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_disability", "requiresDisability"))
    requiredDisabilityType: Optional[str] = Field(None, validation_alias=AliasChoices("required_disability_type", "requiredDisabilityType"))
    
    requiresMedicalCareChild: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_medical_care_child", "requiresMedicalCareChild"))
    requiresYoungCarer: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_young_carer", "requiresYoungCarer"))
    requiresHouseholdHead: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_household_head", "requiresHouseholdHead"))
    requiresRent: Optional[bool] = Field(None, validation_alias=AliasChoices("requires_rent", "requiresRent"))
    
    conditionDescription: Optional[str] = Field(None, validation_alias=AliasChoices("condition_description", "conditionDescription"))
    conditionTextOriginal: Optional[str] = Field(None, validation_alias=AliasChoices("condition_text_original", "conditionTextOriginal"))
    manualCheckRequired: bool = Field(False, validation_alias=AliasChoices("manual_check_required", "manualCheckRequired"))

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProgramConditionCreateRequest(BaseModel):
    minAge: Optional[int] = None
    maxAge: Optional[int] = None
    maxAnnualIncome: Optional[int] = None
    maxMonthlyIncome: Optional[int] = None
    maxSavingsAmount: Optional[int] = None
    requiresTaxExempt: Optional[bool] = None
    requiresChildren: Optional[bool] = None
    minChildrenCount: Optional[int] = None
    requiresSingleParent: Optional[bool] = None
    requiredGender: Optional[str] = None
    requiredCity: Optional[str] = None
    requiredWard: Optional[str] = None
    requiresUnemployed: Optional[bool] = None
    unemployedWithinMonths: Optional[int] = None
    requiresJobSeeking: Optional[bool] = None
    requiresIncomeDecreased: Optional[bool] = None
    requiresHealthInsurance: Optional[bool] = None
    requiresPregnancy: Optional[bool] = None
    maxPostpartumMonths: Optional[int] = None
    requiresDisability: Optional[bool] = None
    requiredDisabilityType: Optional[str] = None
    requiresMedicalCareChild: Optional[bool] = None
    requiresYoungCarer: Optional[bool] = None
    requiresHouseholdHead: Optional[bool] = None
    requiresRent: Optional[bool] = None
    conditionDescription: Optional[str] = None
    conditionTextOriginal: Optional[str] = None
    manualCheckRequired: bool = False


class ProgramSourceCreateRequest(BaseModel):
    sourceUrl: str
    sourceType: str
    title: Optional[str] = None
    publisher: Optional[str] = None
    publishedAt: Optional[date] = None
    lastModifiedAt: Optional[date] = None
    notes: Optional[str] = None


class ProgramCreateRequest(BaseModel):
    title: str
    provider: str
    summary: str
    benefit: Optional[str] = None
    category: Optional[str] = None
    supportType: Optional[str] = None
    benefitAmountType: Optional[str] = None
    benefitAmount: Optional[int] = None
    benefitUnit: Optional[str] = None
    targetPrefecture: Optional[str] = None
    targetCity: Optional[str] = None
    targetWard: Optional[str] = None
    applicationRequired: Optional[bool] = None
    applicationMethod: Optional[str] = None
    applicationPeriodType: Optional[str] = None
    applicationUrl: Optional[str] = None
    deadline: Optional[date] = None
    confidenceLevel: Optional[str] = None
    isActive: bool = True
    condition: Optional[ProgramConditionCreateRequest] = None
    sources: List[ProgramSourceCreateRequest] = []


class ProgramUpdateRequest(BaseModel):
    title: Optional[str] = None
    provider: Optional[str] = None
    summary: Optional[str] = None
    benefit: Optional[str] = None
    category: Optional[str] = None
    supportType: Optional[str] = None
    benefitAmountType: Optional[str] = None
    benefitAmount: Optional[int] = None
    benefitUnit: Optional[str] = None
    targetPrefecture: Optional[str] = None
    targetCity: Optional[str] = None
    targetWard: Optional[str] = None
    applicationRequired: Optional[bool] = None
    applicationMethod: Optional[str] = None
    applicationPeriodType: Optional[str] = None
    applicationUrl: Optional[str] = None
    deadline: Optional[date] = None
    confidenceLevel: Optional[str] = None
    isActive: Optional[bool] = None
    condition: Optional[ProgramConditionCreateRequest] = None
    sources: Optional[List[ProgramSourceCreateRequest]] = None


class ProgramSourceResponse(BaseModel):
    id: int
    sourceUrl: str = Field(..., validation_alias=AliasChoices("source_url", "sourceUrl"))
    sourceType: str = Field(..., validation_alias=AliasChoices("source_type", "sourceType"))
    title: Optional[str] = None
    publisher: Optional[str] = None
    publishedAt: Optional[date] = Field(None, validation_alias=AliasChoices("published_at", "publishedAt"))
    lastModifiedAt: Optional[date] = Field(None, validation_alias=AliasChoices("last_modified_at", "lastModifiedAt"))
    fetchedAt: Optional[datetime] = Field(None, validation_alias=AliasChoices("fetched_at", "fetchedAt"))
    checkedAt: Optional[datetime] = Field(None, validation_alias=AliasChoices("checked_at", "checkedAt"))
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProgramRequiredDocumentResponse(BaseModel):
    id: int
    documentName: str = Field(..., validation_alias=AliasChoices("document_name", "documentName"))
    isRequired: bool = Field(True, validation_alias=AliasChoices("is_required", "isRequired"))
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProgramListItemResponse(BaseModel):
    id: int
    title: str
    provider: str
    summary: str
    benefit: Optional[str] = None
    category: Optional[str] = None
    
    supportType: Optional[str] = Field(None, validation_alias=AliasChoices("support_type", "supportType"))
    benefitAmountType: Optional[str] = Field(None, validation_alias=AliasChoices("benefit_amount_type", "benefitAmountType"))
    benefitAmount: Optional[int] = Field(None, validation_alias=AliasChoices("benefit_amount", "benefitAmount"))
    benefitUnit: Optional[str] = Field(None, validation_alias=AliasChoices("benefit_unit", "benefitUnit"))
    
    targetPrefecture: Optional[str] = Field(None, validation_alias=AliasChoices("target_prefecture", "targetPrefecture"))
    targetCity: Optional[str] = Field(None, validation_alias=AliasChoices("target_city", "targetCity"))
    targetWard: Optional[str] = Field(None, validation_alias=AliasChoices("target_ward", "targetWard"))
    
    applicationRequired: Optional[bool] = Field(None, validation_alias=AliasChoices("application_required", "applicationRequired"))
    applicationMethod: Optional[str] = Field(None, validation_alias=AliasChoices("application_method", "applicationMethod"))
    applicationPeriodType: Optional[str] = Field(None, validation_alias=AliasChoices("application_period_type", "applicationPeriodType"))
    applicationUrl: Optional[str] = Field(None, validation_alias=AliasChoices("application_url", "applicationUrl"))
    deadline: Optional[date] = None
    confidenceLevel: Optional[str] = Field(None, validation_alias=AliasChoices("confidence_level", "confidenceLevel"))
    isActive: bool = Field(True, validation_alias=AliasChoices("is_active", "isActive"))

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProgramDetailResponse(ProgramListItemResponse):
    startDate: Optional[date] = Field(None, validation_alias=AliasChoices("start_date", "startDate"))
    endDate: Optional[date] = Field(None, validation_alias=AliasChoices("end_date", "endDate"))
    requiredDocuments: Optional[str] = Field(None, validation_alias=AliasChoices("required_documents", "requiredDocuments"))
    contactDepartment: Optional[str] = Field(None, validation_alias=AliasChoices("contact_department", "contactDepartment"))
    contactPhone: Optional[str] = Field(None, validation_alias=AliasChoices("contact_phone", "contactPhone"))
    sourceUrl: Optional[str] = Field(None, validation_alias=AliasChoices("source_url", "sourceUrl"))
    sourceUpdatedAt: Optional[date] = Field(None, validation_alias=AliasChoices("source_updated_at", "sourceUpdatedAt"))
    dataConfirmedAt: Optional[date] = Field(None, validation_alias=AliasChoices("data_confirmed_at", "dataConfirmedAt"))
    notes: Optional[str] = None
    
    condition: Optional[ProgramConditionResponse] = None
    sources: List[ProgramSourceResponse] = Field(default_factory=list)
    requiredDocumentItems: List[ProgramRequiredDocumentResponse] = Field(default_factory=list, validation_alias=AliasChoices("required_document_items", "requiredDocumentItems"))

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
