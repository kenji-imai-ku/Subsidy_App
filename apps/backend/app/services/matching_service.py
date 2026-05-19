from datetime import date
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories import profile_repository, program_repository


def calculate_age(birth_date: date, today: date | None = None) -> int:
    if today is None:
        today = date.today()

    age = today.year - birth_date.year

    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age


def calculate_match_score(profile, program, condition):
    # TODO(v2 matching):
    # v2で追加された profile_employment_statuses,
    # profile_special_conditions,
    # support_program_conditions の拡張項目を使って、
    # マッチング条件を段階的に追加する。
    
    score = 0
    reasons = []
    warnings = []
    failed_required_conditions = []

    age = calculate_age(profile.birth_date) if profile.birth_date else None

    # -------------------------
    # 1. 地域条件: 30点
    # -------------------------
    if program.target_prefecture:
        if program.target_prefecture == profile.prefecture:
            score += 30
            reasons.append("居住地が対象都道府県に含まれています")
        else:
            failed_required_conditions.append("対象都道府県が一致しません")
    else:
        score += 30
        reasons.append("全国または地域指定なしの制度です")

    # 市区町村/区の判定はMVPでは警告に留める
    if program.target_city:
        warnings.append("市区町村単位の対象条件は公式情報の確認が必要です")
    if program.target_ward:
        warnings.append("区単位の対象条件は公式情報の確認が必要です")

    # -------------------------
    # 2. 年齢条件: 20点
    # -------------------------
    has_age_condition = condition and (
        condition.min_age is not None or condition.max_age is not None
    )

    if has_age_condition:
        if age is None:
            warnings.append("年齢条件の確認が必要です")
        elif condition.min_age is not None and age < condition.min_age:
            failed_required_conditions.append("最低年齢条件を満たしていません")
        elif condition.max_age is not None and age > condition.max_age:
            failed_required_conditions.append("最高年齢条件を満たしていません")
        else:
            score += 20
            reasons.append("年齢条件を満たしている可能性があります")
    else:
        score += 20
        reasons.append("年齢条件の指定がありません")

    # -------------------------
    # 3. 所得・税条件: 30点
    # -------------------------
    income_tax_score = 0

    # 所得上限の判定
    if condition and condition.max_annual_income is not None:
        if profile.annual_income_max is None:
            warnings.append("所得条件の確認が必要です")
        elif profile.annual_income_max <= condition.max_annual_income:
            income_tax_score += 15
            reasons.append("所得条件を満たしている可能性があります")
        else:
            # 所得帯の上限で比較しているため、完全に断定しすぎない
            failed_required_conditions.append("所得制限を満たさない可能性があります")
    else:
        income_tax_score += 15
        reasons.append("所得上限の指定がありません")

    # 非課税世帯の判定
    if condition and condition.requires_tax_exempt is True:
        if profile.is_tax_exempt_household is True:
            income_tax_score += 15
            reasons.append("非課税世帯条件を満たしています")
        elif profile.is_tax_exempt_household is None:
            warnings.append("非課税世帯に該当するか確認が必要です")
        else:
            failed_required_conditions.append("非課税世帯向けの制度です")
    else:
        income_tax_score += 15
        reasons.append("非課税世帯条件の指定がありません")

    score += income_tax_score

    # -------------------------
    # 4. 世帯・属性条件: 20点
    # -------------------------
    household_score = 0

    # 子どもの有無
    if condition and condition.requires_children is True:
        if profile.has_children:
            household_score += 10
            reasons.append("子どもがいる世帯向け条件を満たしています")
        else:
            failed_required_conditions.append("子どもがいる世帯向けの制度です")
    else:
        household_score += 10
        reasons.append("子どもの有無に関する条件指定がありません")

    # 子どもの人数 (加点・判定要素)
    if condition and condition.min_children_count is not None:
        if profile.children_count < condition.min_children_count:
            failed_required_conditions.append("子どもの人数条件を満たしていません")

    # ひとり親
    if condition and condition.requires_single_parent is True:
        if profile.is_single_parent is True:
            household_score += 5
            reasons.append("ひとり親世帯の条件を満たしています")
        elif profile.is_single_parent is None:
            warnings.append("ひとり親世帯に該当するか確認が必要です")
        else:
            failed_required_conditions.append("ひとり親世帯向けの制度です")
    else:
        household_score += 5
        reasons.append("ひとり親に関する条件指定がありません")

    # 性別
    if condition and condition.required_gender is not None:
        if profile.gender == condition.required_gender:
            household_score += 5
            reasons.append("性別条件を満たしています")
        elif profile.gender == "no_answer":
            warnings.append("性別に関する対象条件の確認が必要です")
        else:
            failed_required_conditions.append("性別条件を満たしていません")
    else:
        household_score += 5
        reasons.append("性別に関する条件指定がありません")

    score += household_score

    # -------------------------
    # 5. 特殊条件・人間確認: (v2拡張)
    # -------------------------
    if condition and getattr(condition, "manual_check_required", False):
        warnings.append("詳細な対象条件は、自治体の窓口等で確認が必要です")

    # -------------------------
    # 6. 判定結果の集約
    # -------------------------
    if failed_required_conditions:
        return None

    status = "possible" if warnings else "eligible"

    return {
        "program": program,
        "score": min(score, 100),
        "status": status,
        "reasons": reasons,
        "warnings": warnings,
    }


def get_matches(db: Session):
    profile = profile_repository.get_current_profile(db)

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    programs = program_repository.list_programs_with_conditions(db)

    results = []

    for program in programs:
        result = calculate_match_score(profile, program, program.condition)
        if result is not None:
            results.append(result)

    # スコア降順にソート
    results.sort(key=lambda x: x["score"], reverse=True)

    return results
