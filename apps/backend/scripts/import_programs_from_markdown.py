import os
import sys
import json
import argparse
import hashlib
from pathlib import Path
from enum import Enum
from typing import List, Optional, Dict, Any, Type
from datetime import date

from pydantic import BaseModel, Field, ValidationError, ConfigDict
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated

from openai import OpenAI
from sqlalchemy.orm import Session

# --- Path Setup ---
# Add the apps/backend directory to sys.path to allow imports from app.*
current_dir = Path(__file__).resolve().parent.parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.support_program import SupportProgram
from app.schemas.support_program import ProgramCreateRequest, ProgramConditionCreateRequest, ProgramSourceCreateRequest
from app.services import program_service

# --- Enum Definitions ---

class SupportType(str, Enum):
    cash = "cash"
    subsidy = "subsidy"
    medical = "medical"
    service_discount = "service_discount"
    service_dispatch = "service_dispatch"
    loan = "loan"
    goods = "goods"
    consultation = "consultation"
    tax_reduction = "tax_reduction"
    other = "other"
    unknown = "unknown"

class BenefitAmountType(str, Enum):
    fixed = "fixed"
    max_amount = "max_amount"
    depends = "depends"
    free_text = "free_text"
    unknown = "unknown"

class BenefitUnit(str, Enum):
    per_person = "per_person"
    per_child = "per_child"
    per_household = "per_household"
    per_month = "per_month"
    per_use = "per_use"
    one_time = "one_time"
    other = "other"
    unknown = "unknown"

class ApplicationMethod(str, Enum):
    online = "online"
    mail = "mail"
    counter = "counter"
    automatic = "automatic"
    not_required = "not_required"
    unknown = "unknown"

class ApplicationPeriodType(str, Enum):
    always = "always"
    deadline = "deadline"
    limited = "limited"
    unknown = "unknown"

class ConfidenceLevel(str, Enum):
    official = "official"
    manual_checked = "manual_checked"
    estimated = "estimated"
    dummy = "dummy"

# --- Alias Mappings ---

SUPPORT_TYPE_MAP = {
    "給付金": "cash", "手当": "cash", "現金給付": "cash",
    "補助金": "subsidy", "助成金": "subsidy", "補助・助成": "subsidy",
    "医療費助成": "medical", "医療費補助": "medical", "医療": "medical",
    "サービス割引": "service_discount", "割引": "service_discount", "利用料減額": "service_discount",
    "サービス派遣": "service_dispatch", "派遣": "service_dispatch", "ヘルパー派遣": "service_dispatch",
    "貸付": "loan", "貸付金": "loan",
    "物品支給": "goods", "現物給付": "goods",
    "相談": "consultation", "相談支援": "consultation",
    "減免": "tax_reduction", "税減免": "tax_reduction",
    "その他": "other",
    "不明": "unknown"
}

BENEFIT_AMOUNT_TYPE_MAP = {
    "固定": "fixed", "固定額": "fixed",
    "上限": "max_amount", "上限額": "max_amount",
    "条件による": "depends", "場合による": "depends", "変動": "depends",
    "自由記述": "free_text", "複雑": "free_text",
    "不明": "unknown"
}

APPLICATION_METHOD_MAP = {
    "オンライン": "online", "Web": "online", "ウェブ": "online",
    "郵送": "mail",
    "窓口": "counter", "窓口申請": "counter",
    "自動": "automatic", "自動給付": "automatic",
    "申請不要": "not_required", "不要": "not_required",
    "不明": "unknown"
}

BENEFIT_UNIT_MAP = {
    "1人あたり": "per_person", "一人当たり": "per_person",
    "子ども1人あたり": "per_child", "子供一人当たり": "per_child",
    "1世帯あたり": "per_household", "一世帯当たり": "per_household",
    "月額": "per_month", "毎月": "per_month",
    "1回あたり": "per_use", "一回あたり": "per_use",
    "1回限り": "one_time", "一回限り": "one_time",
    "その他": "other",
    "不明": "unknown"
}

APPLICATION_PERIOD_TYPE_MAP = {
    "随時": "always", "いつでも": "always",
    "締切あり": "deadline", "期限あり": "deadline",
    "期間限定": "limited", "期間指定": "limited",
    "不明": "unknown"
}

def normalize_value(value: Any, mapping: Dict[str, str], enum_class: Type[Enum]) -> str:
    if value is None:
        return enum_class.unknown.value
    
    val_str = str(value).strip()
    
    # 既にEnum値（英語）に一致する場合はそのまま返す
    if val_str in [e.value for e in enum_class]:
        return val_str
    
    # マッピング辞書から探す（部分一致も考慮）
    for k, v in mapping.items():
        if k in val_str:
            return v
            
    return enum_class.unknown.value

# --- Candidate Schemas ---

def validate_support_type(v): return normalize_value(v, SUPPORT_TYPE_MAP, SupportType)
def validate_benefit_amount_type(v): return normalize_value(v, BENEFIT_AMOUNT_TYPE_MAP, BenefitAmountType)
def validate_application_method(v): return normalize_value(v, APPLICATION_METHOD_MAP, ApplicationMethod)
def validate_benefit_unit(v): return normalize_value(v, BENEFIT_UNIT_MAP, BenefitUnit)
def validate_application_period_type(v): return normalize_value(v, APPLICATION_PERIOD_TYPE_MAP, ApplicationPeriodType)

class ProgramConditionCandidate(BaseModel):
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    max_annual_income: Optional[int] = None
    requires_tax_exempt: Optional[bool] = None
    requires_children: Optional[bool] = None
    min_children_count: Optional[int] = None
    requires_single_parent: Optional[bool] = None
    required_gender: Optional[str] = None
    required_city: Optional[str] = None
    required_ward: Optional[str] = None
    requires_unemployed: Optional[bool] = None
    requires_job_seeking: Optional[bool] = None
    requires_income_decreased: Optional[bool] = None
    requires_health_insurance: Optional[bool] = None
    requires_pregnancy: Optional[bool] = None
    max_postpartum_months: Optional[int] = None
    requires_disability: Optional[bool] = None
    requires_rent: Optional[bool] = None
    condition_description: Optional[str] = None
    condition_text_original: Optional[str] = None
    manual_check_required: bool = False

class ProgramExtractionCandidate(BaseModel):
    title: str = Field(..., description="支援制度の名称")
    provider: str = Field(..., description="実施主体（自治体名、国、団体名など）")
    summary: str = Field(..., description="制度の簡潔な概要")
    benefit: Optional[str] = Field(None, description="支給内容の詳細説明")
    category: Optional[str] = Field(None, description="制度のカテゴリ（例: 子育て、介護、住宅など）")
    support_type: Annotated[SupportType, BeforeValidator(validate_support_type)] = Field(SupportType.unknown, description="支援の種類（cash, subsidyなど）")
    benefit_amount_type: Annotated[BenefitAmountType, BeforeValidator(validate_benefit_amount_type)] = Field(BenefitAmountType.unknown, description="金額の種類（fixed, max_amountなど）")
    benefit_amount: Optional[int] = Field(None, description="金額（数値のみ、不明または複雑な場合はnull）")
    benefit_unit: Annotated[BenefitUnit, BeforeValidator(validate_benefit_unit)] = Field(BenefitUnit.unknown, description="金額の単位（per_person, per_householdなど）")
    target_prefecture: Optional[str] = Field(None, description="対象都道府県")
    target_city: Optional[str] = Field(None, description="対象市区町村")
    target_ward: Optional[str] = Field(None, description="対象区（政令指定都市の場合）")
    application_required: Optional[bool] = Field(None, description="申請が必要かどうか")
    application_method: Annotated[ApplicationMethod, BeforeValidator(validate_application_method)] = Field(ApplicationMethod.unknown, description="申請方法")
    application_period_type: Annotated[ApplicationPeriodType, BeforeValidator(validate_application_period_type)] = Field(ApplicationPeriodType.unknown, description="申請期間のタイプ（always, deadlineなど）")
    application_url: Optional[str] = Field(None, description="申請先URLまたは詳細URL")
    deadline: Optional[date] = Field(None, description="申請締切日（YYYY-MM-DD形式、不明ならnull）")
    contact_department: Optional[str] = Field(None, description="問い合わせ部署")
    contact_phone: Optional[str] = Field(None, description="問い合わせ電話番号")
    condition: Optional[ProgramConditionCandidate] = Field(None, description="申請条件の構造化データ")
    confidence_level: ConfidenceLevel = Field(ConfidenceLevel.estimated, description="信頼度（原則 estimated）")
    uncertain_fields: List[str] = Field(default_factory=list, description="不確実なフィールド名のリスト")
    evidence: str = Field(..., description="抽出根拠（原文の引用または要約）")

    model_config = ConfigDict(populate_by_name=True)

# --- LLM Processing ---

SYSTEM_PROMPT = """
あなたは自治体や国の支援制度情報を抽出する専門家です。
与えられたMarkdown形式の支援制度ページから情報を抽出し、指定されたJSON形式で出力してください。

## ルール:
1. JSONのみを返してください。
2. 本文に明記されていない項目は null にしてください。
3. 推測で条件を埋めないでください。
4. Enum項目（support_type, benefit_amount_type, application_method, benefit_unit, application_period_type）については、
   許可された値（英語）を推測して入れるか、対応する日本語（例：「給付金」「窓口」「1世帯あたり」「随時」）を入れてください。
   プログラム側で自動的に正規化します。
5. 金額（benefit_amount）が明確に数値として取れる場合のみ数値を入れてください。カンマなどは除いてください。
6. 金額が複雑な場合は benefit_amount_type を 'depends' または 'free_text' にし、benefit フィールドに詳細を記述してください。
7. 日付（deadline）は YYYY-MM-DD 形式で抽出してください。不明な場合は null にしてください。
8. confidence_level は原則 'estimated' にしてください。
9. evidence には、抽出根拠となる原文の短い引用または該当箇所の要約を入れてください。
10. uncertain_fields には、不確実な項目名を入れてください。
11. manual_check_required は、条件が複雑・曖昧・原文確認が必要な場合は true にしてください。
12. 申請条件（condition）は、可能な限り細かく抽出してください。
"""

def get_extract_prompt(content: str) -> str:
    return f"以下のMarkdownから支援制度情報を抽出してください:\n\n{content}"

def get_retry_prompt(original_json: str, error_msg: str) -> str:
    return f"""
前回の出力において以下のバリデーションエラーが発生しました:
{error_msg}

以下のJSONを修正して、正しい形式で出力してください。
許可されたEnum値（またはそれに近い日本語）を使用してください。
不明な値は null または 'unknown' にしてください。

元のJSON:
{original_json}
"""

def call_llm(client: OpenAI, messages: List[Dict[str, str]]) -> ProgramExtractionCandidate:
    response = client.beta.chat.completions.parse(
        model=settings.openai_model,
        messages=messages,
        response_format=ProgramExtractionCandidate,
    )
    return response.choices[0].message.parsed

# --- Main Script Logic ---

def process_file(file_path: Path, client: OpenAI, db: Session, dry_run: bool) -> (bool, str):
    print(f"[*] Processing {file_path.name}...")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        return False, f"File read error: {str(e)}"
    
    if not content:
        return False, "Empty file"

    # Step 1: LLM Extraction with Retry
    extracted_data = None
    last_error = ""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": get_extract_prompt(content)}
    ]

    for attempt in range(3): # Initial + 2 retries
        try:
            extracted_data = call_llm(client, messages)
            break
        except Exception as e:
            last_error = str(e)
            print(f"    [!] Attempt {attempt + 1} failed: {last_error}")
            if attempt < 2:
                # バリデーションエラーの内容と、(もし取得できれば)失敗したJSONを渡して修正を促す
                # beta.parse では pydantic のエラーが含まれるため、それを get_retry_prompt に渡す
                retry_msg = f"バリデーションエラーが発生しました。指示に従ってJSONを修正してください。\nエラー内容: {last_error}"
                messages.append({"role": "user", "content": retry_msg})
            else:
                return False, f"LLM Extraction failed after retries: {last_error}"

    if not extracted_data:
        return False, "Failed to extract data"

    # Step 2: Map to DB Schema (Moved up to support detailed preview in dry-run)
    condition_data = None
    if extracted_data.condition:
        # Convert snake_case to camelCase for ProgramConditionCreateRequest
        condition_dict = extracted_data.condition.model_dump()
        
        # Mapping helper
        def to_camel(snake_str):
            components = snake_str.split('_')
            return components[0] + ''.join(x.title() for x in components[1:])

        condition_data_camel = {to_camel(k): v for k, v in condition_dict.items()}
        condition_data = ProgramConditionCreateRequest(**condition_data_camel)

    sources = [
        ProgramSourceCreateRequest(
            sourceUrl=extracted_data.application_url or f"file://{file_path.name}",
            sourceType="official_site",
            title=extracted_data.title,
            notes=f"Extracted from {file_path.name}"
        )
    ]

    program_request = ProgramCreateRequest(
        title=extracted_data.title,
        provider=extracted_data.provider,
        summary=extracted_data.summary,
        benefit=extracted_data.benefit,
        category=extracted_data.category,
        supportType=extracted_data.support_type.value,
        benefitAmountType=extracted_data.benefit_amount_type.value,
        benefitAmount=extracted_data.benefit_amount,
        benefitUnit=extracted_data.benefit_unit.value,
        targetPrefecture=extracted_data.target_prefecture,
        targetCity=extracted_data.target_city,
        targetWard=extracted_data.target_ward,
        applicationRequired=extracted_data.application_required,
        applicationMethod=extracted_data.application_method.value,
        applicationPeriodType=extracted_data.application_period_type.value,
        applicationUrl=extracted_data.application_url,
        deadline=extracted_data.deadline,
        confidenceLevel=extracted_data.confidence_level.value,
        isActive=True,
        condition=condition_data,
        sources=sources
    )

    if dry_run:
        print(f"    [Dry-run] Detailed Extraction for: {extracted_data.title}")
        print("-" * 40)
        print("1. LLM Extracted Data (Raw):")
        print(json.dumps(extracted_data.model_dump(), indent=2, ensure_ascii=False, default=str))
        print("\n2. DB Registration Request (Normalized):")
        print(json.dumps(program_request.model_dump(), indent=2, ensure_ascii=False, default=str))
        print("-" * 40)
        return True, "Success (Dry-run preview)"

    # Step 3: Check for Duplicates (Only for actual import)
    existing = db.query(SupportProgram).filter(
        SupportProgram.title == extracted_data.title,
        SupportProgram.provider == extracted_data.provider
    ).first()
    
    if existing:
        return False, "Duplicate program (same title and provider)"

    try:
        db_program = program_service.create_program(db, program_request)
        return True, f"Registered with ID: {db_program.id}"
    except Exception as e:
        db.rollback()
        return False, f"DB Error: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Markdownファイルから支援制度情報を抽出してDBに登録するスクリプト")
    parser.add_argument("--dry-run", action="store_true", help="DB登録を行わず、抽出結果のみ表示します")
    parser.add_argument("--file", type=str, help="特定のMarkdownファイルのみ処理します")
    args = parser.parse_args()

    if not settings.openai_api_key:
        print("[!] Error: OPENAI_API_KEY is not set in .env or environment.")
        sys.exit(1)

    client = OpenAI(api_key=settings.openai_api_key)
    db = SessionLocal()

    # Get the directory where the script is located, then go up to apps/backend
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "output"
    
    if not output_dir.exists():
        print(f"[!] Error: Directory {output_dir} not found.")
        sys.exit(1)

    files_to_process = []
    if args.file:
        f_path = Path(args.file)
        if not f_path.exists():
            # Try relative to output_dir if not found
            f_path = output_dir / args.file
        
        if f_path.exists() and f_path.suffix == ".md":
            files_to_process = [f_path]
        else:
            print(f"[!] Error: File {args.file} not found or not a .md file.")
            sys.exit(1)
    else:
        files_to_process = sorted(list(output_dir.glob("*.md")))

    if not files_to_process:
        print("[*] No Markdown files found to process.")
        return

    print(f"[*] Starting processing {len(files_to_process)} files...")
    if args.dry_run:
        print("[*] MODE: DRY-RUN (No database changes will be made)")

    stats = {"total": len(files_to_process), "success": 0, "skipped": 0, "failed": 0}
    results = []

    for file_path in files_to_process:
        success, message = process_file(file_path, client, db, args.dry_run)
        
        if success:
            stats["success"] += 1
            print(f"    [+] SUCCESS: {message}")
        else:
            if "Duplicate" in message or "Empty" in message:
                stats["skipped"] += 1
                print(f"    [-] SKIPPED: {message}")
            else:
                stats["failed"] += 1
                print(f"    [!] FAILED: {message}")
        
        results.append({
            "file": file_path.name,
            "status": "SUCCESS" if success else ("SKIPPED" if ("Duplicate" in message or "Empty" in message) else "FAILED"),
            "message": message
        })

    print("\n" + "="*60)
    print("処理結果サマリー:")
    print(f"  総ファイル数: {stats['total']}")
    print(f"  成功件数:     {stats['success']}")
    print(f"  スキップ件数: {stats['skipped']}")
    print(f"  失敗件数:     {stats['failed']}")
    print("="*60)

    if stats["failed"] > 0:
        print("\n失敗詳細:")
        for r in results:
            if r["status"] == "FAILED":
                print(f"  - {r['file']}: {r['message']}")

if __name__ == "__main__":
    main()
