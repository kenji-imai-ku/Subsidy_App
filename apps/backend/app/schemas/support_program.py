from datetime import date
from pydantic import BaseModel
from typing import Optional


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

    class Config:
        from_attributes = True


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

    # SQLAlchemyのモデル属性名とPydanticのフィールド名が異なる場合の変換（エイリアス）
    # ただし今回はシンプルにするため、一旦手動変換またはそのまま返す方針で行きます。
    # RoleBのドキュメントに合わせたCamelCase形式のレスポンスを提供します。


class ProgramDetailResponse(ProgramListItemResponse):
    requiredDocuments: Optional[str] = None
    sourceUrl: Optional[str] = None
    condition: Optional[ProgramConditionResponse] = None
