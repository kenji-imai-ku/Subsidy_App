from datetime import date
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import Optional, Any


class ProgramConditionResponse(BaseModel):
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    max_annual_income: Optional[int] = None
    requires_tax_exempt: Optional[bool] = None
    requires_children: Optional[bool] = None
    min_children_count: Optional[int] = None
    requires_single_parent: Optional[bool] = None
    required_gender: Optional[str] = None
    condition_description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProgramListItemResponse(BaseModel):
    id: int
    title: str
    provider: str
    summary: str
    benefit: Optional[str] = None
    category: Optional[str] = None
    targetPrefecture: Optional[str] = None
    targetCity: Optional[str] = None
    targetWard: Optional[str] = None
    applicationUrl: Optional[str] = None
    deadline: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def map_snake_to_camel(cls, data: Any) -> Any:
        if hasattr(data, "target_prefecture"):
            # SQLAlchemyモデルからの変換
            return {
                "id": data.id,
                "title": data.title,
                "provider": data.provider,
                "summary": data.summary,
                "benefit": data.benefit,
                "category": data.category,
                "targetPrefecture": data.target_prefecture,
                "targetCity": data.target_city,
                "targetWard": data.target_ward,
                "applicationUrl": data.application_url,
                "deadline": data.deadline,
            }
        return data


class ProgramDetailResponse(ProgramListItemResponse):
    requiredDocuments: Optional[str] = None
    sourceUrl: Optional[str] = None
    condition: Optional[ProgramConditionResponse] = None

    @model_validator(mode='before')
    @classmethod
    def map_snake_to_camel_detail(cls, data: Any) -> Any:
        if hasattr(data, "target_prefecture"):
            return {
                "id": data.id,
                "title": data.title,
                "provider": data.provider,
                "summary": data.summary,
                "benefit": data.benefit,
                "category": data.category,
                "targetPrefecture": data.target_prefecture,
                "targetCity": data.target_city,
                "targetWard": data.target_ward,
                "applicationUrl": data.application_url,
                "deadline": data.deadline,
                "requiredDocuments": data.required_documents,
                "sourceUrl": data.source_url,
                "condition": data.condition,
            }
        return data
