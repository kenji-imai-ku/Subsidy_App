from datetime import date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.profile import ProfileRequest
from app.repositories import profile_repository


INCOME_MAX_MAP = {
    "200万円未満": 2_000_000,
    "200万円〜400万円未満": 4_000_000,
    "400万円〜600万円未満": 6_000_000,
    "600万円〜800万円未満": 8_000_000,
    "800万円〜1,000万円未満": 10_000_000,
    "1,000万円以上": None,
}

GENDER_MAP = {
    "男性": "male",
    "女性": "female",
    "その他": "other",
    "回答しない": "no_answer",
}

TAX_EXEMPT_MAP = {
    "はい": True,
    "いいえ": False,
    "わからない": None,
}

FAMILY_MAP = {
    "独身": {"has_spouse": False, "is_single_parent": False},
    "配偶者あり": {"has_spouse": True, "is_single_parent": False},
    "ひとり親": {"has_spouse": False, "is_single_parent": True},
    "その他": {"has_spouse": None, "is_single_parent": None},
}

HOUSING_STATUS_MAP = {
    "持ち家": "owned",
    "賃貸": "rented",
    "公営住宅": "public_housing",
    "家族と同居（実家等）": "living_with_family",
    "その他": "other",
    "わからない": "unknown",
}

GENDER_REVERSE_MAP = {
    "male": "男性",
    "female": "女性",
    "other": "その他",
    "no_answer": "回答しない",
}

TAX_EXEMPT_REVERSE_MAP = {
    True: "はい",
    False: "いいえ",
    None: "わからない",
}


def convert_profile_request(request: ProfileRequest) -> dict:
    try:
        birth_date = date(
            int(request.birthYear),
            int(request.birthMonth),
            int(request.birthDay),
        )
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid birth date")

    if request.householdIncome not in INCOME_MAX_MAP:
        raise HTTPException(status_code=422, detail="Invalid householdIncome")

    # Handle gender conversion
    gender_val = GENDER_MAP.get(request.gender, request.gender)
    
    # Handle taxExempt conversion
    tax_exempt_val = TAX_EXEMPT_MAP.get(request.taxExempt, None)
    if request.taxExempt not in TAX_EXEMPT_MAP:
         if str(request.taxExempt).lower() == "true":
             tax_exempt_val = True
         elif str(request.taxExempt).lower() == "false":
             tax_exempt_val = False

    if request.familyType not in FAMILY_MAP:
        raise HTTPException(status_code=422, detail="Invalid familyType")

    try:
        children_count = int(request.childrenCount or 0)
    except ValueError:
        raise HTTPException(status_code=422, detail="childrenCount must be number")

    if children_count < 0:
        raise HTTPException(status_code=422, detail="childrenCount must be 0 or more")

    family_values = FAMILY_MAP[request.familyType]
    
    housing_status_val = HOUSING_STATUS_MAP.get(request.housingStatus, request.housingStatus)

    data = {
        "name": request.name,
        "prefecture": request.prefecture,
        "city": request.city,
        "ward": request.ward,
        "birth_date": birth_date,
        "gender": gender_val,
        "household_income_label": request.householdIncome,
        "annual_income_max": INCOME_MAX_MAP[request.householdIncome],
        "monthly_income": request.monthlyIncome,
        "savings_amount_range": request.savingsAmountRange,
        "housing_status": housing_status_val,
        "family_type": request.familyType,
        "has_spouse": request.hasSpouse if request.hasSpouse is not None else family_values["has_spouse"],
        "children_count": children_count,
        "has_children": children_count > 0,
        "is_single_parent": family_values["is_single_parent"],
        "is_tax_exempt_household": tax_exempt_val,
        "is_household_head": request.isHouseholdHead,
    }

    if request.employment:
        data["employment"] = {
            "employment_status": request.employment.employmentStatus,
            "is_unemployed": request.employment.isUnemployed,
            "unemployed_since": request.employment.unemployedSince,
            "is_job_seeking": request.employment.isJobSeeking,
            "income_decreased": request.employment.incomeDecreased,
            "income_decreased_reason": request.employment.incomeDecreasedReason,
        }

    if request.specialConditions:
        data["special_conditions"] = {
            "has_health_insurance": request.specialConditions.hasHealthInsurance,
            "is_pregnant": request.specialConditions.isPregnant,
            "postpartum_months": request.specialConditions.postpartumMonths,
            "has_disability": request.specialConditions.hasDisability,
            "disability_type": request.specialConditions.disabilityType,
            "disability_grade": request.specialConditions.disabilityGrade,
            "has_medical_care_child": request.specialConditions.hasMedicalCareChild,
            "has_care_required_family": request.specialConditions.hasCareRequiredFamily,
            "has_young_carer_in_household": request.specialConditions.hasYoungCarerInHousehold,
        }

    return data


def get_profile(db: Session):
    profile = profile_repository.get_current_profile(db)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


def upsert_profile(db: Session, request: ProfileRequest):
    data = convert_profile_request(request)
    profile = profile_repository.get_current_profile(db)

    if profile is None:
        return profile_repository.create_profile(db, data)

    return profile_repository.update_profile(db, profile, data)


def to_profile_response(profile):
    employment = None
    if profile.employment:
        employment = {
            "employmentStatus": profile.employment.employment_status,
            "isUnemployed": profile.employment.is_unemployed,
            "unemployedSince": profile.employment.unemployed_since,
            "isJobSeeking": profile.employment.is_job_seeking,
            "incomeDecreased": profile.employment.income_decreased,
            "incomeDecreasedReason": profile.employment.income_decreased_reason,
        }

    special_conditions = None
    if profile.special_conditions:
        special_conditions = {
            "hasHealthInsurance": profile.special_conditions.has_health_insurance,
            "isPregnant": profile.special_conditions.is_pregnant,
            "postpartumMonths": profile.special_conditions.postpartum_months,
            "hasDisability": profile.special_conditions.has_disability,
            "disabilityType": profile.special_conditions.disability_type,
            "disabilityGrade": profile.special_conditions.disability_grade,
            "hasMedicalCareChild": profile.special_conditions.has_medical_care_child,
            "hasCareRequiredFamily": profile.special_conditions.has_care_required_family,
            "hasYoungCarerInHousehold": profile.special_conditions.has_young_carer_in_household,
        }

    return {
        "id": profile.id,
        "name": profile.name,
        "prefecture": profile.prefecture,
        "city": profile.city,
        "ward": profile.ward,
        "birthDate": profile.birth_date,
        "gender": GENDER_REVERSE_MAP.get(profile.gender, profile.gender),
        "householdIncome": profile.household_income_label,
        "annualIncomeMax": profile.annual_income_max,
        "monthlyIncome": profile.monthly_income,
        "savingsAmountRange": profile.savings_amount_range,
        "housingStatus": profile.housing_status,
        "familyType": profile.family_type,
        "hasSpouse": profile.has_spouse,
        "childrenCount": profile.children_count,
        "hasChildren": profile.has_children,
        "isSingleParent": profile.is_single_parent,
        "isTaxExemptHousehold": profile.is_tax_exempt_household,
        "isHouseholdHead": profile.is_household_head,
        "employment": employment,
        "specialConditions": special_conditions,
    }
