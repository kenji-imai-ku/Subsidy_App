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

    if request.gender not in GENDER_MAP:
        raise HTTPException(status_code=422, detail="Invalid gender")

    if request.taxExempt not in TAX_EXEMPT_MAP:
        raise HTTPException(status_code=422, detail="Invalid taxExempt")

    if request.familyType not in FAMILY_MAP:
        raise HTTPException(status_code=422, detail="Invalid familyType")

    try:
        children_count = int(request.childrenCount or 0)
    except ValueError:
        raise HTTPException(status_code=422, detail="childrenCount must be number")

    if children_count < 0:
        raise HTTPException(status_code=422, detail="childrenCount must be 0 or more")

    family_values = FAMILY_MAP[request.familyType]

    return {
        "name": request.name,
        "prefecture": request.prefecture,
        "birth_date": birth_date,
        "gender": GENDER_MAP[request.gender],
        "household_income_label": request.householdIncome,
        "annual_income_max": INCOME_MAX_MAP[request.householdIncome],
        "family_type": request.familyType,
        "has_spouse": family_values["has_spouse"],
        "children_count": children_count,
        "has_children": children_count > 0,
        "is_single_parent": family_values["is_single_parent"],
        "is_tax_exempt_household": TAX_EXEMPT_MAP[request.taxExempt],
    }


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
    return {
        "id": profile.id,
        "name": profile.name,
        "prefecture": profile.prefecture,
        "birthDate": profile.birth_date,
        "gender": GENDER_REVERSE_MAP.get(profile.gender, profile.gender),
        "householdIncome": profile.household_income_label,
        "familyType": profile.family_type,
        "childrenCount": profile.children_count,
        "taxExempt": TAX_EXEMPT_REVERSE_MAP.get(profile.is_tax_exempt_household),
    }
