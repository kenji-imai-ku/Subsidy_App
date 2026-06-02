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
    # 初期スコア100点、ステータスは eligible でスタート
    score = 100
    reasons = []
    warnings = []
    status = "eligible"

    age = calculate_age(profile.birth_date) if profile.birth_date else None
    employment = profile.employment
    special = profile.special_conditions

    # -------------------------
    # 1. 地域条件 (都道府県・市区町村・区)
    # -------------------------
    # 都道府県判定 (ハードフィルタ)
    if program.target_prefecture:
        if program.target_prefecture == profile.prefecture:
            reasons.append("居住地が対象都道府県に合致しています")
        else:
            return None  # 都道府県不一致は除外
    else:
        reasons.append("地域指定なし（全国対象）の制度です")

    # 市区町村判定
    if program.target_city:
        if profile.city:
            if program.target_city == profile.city:
                reasons.append(f"居住地が対象市区町村（{profile.city}）に合致しています")
            else:
                return None  # 市区町村不一致は除外
        else:
            # 市区町村指定があるがプロフィールが未入力の場合
            score -= 20
            warnings.append("市区町村単位の対象条件の確認が必要です")
    
    # 区判定
    if program.target_ward:
        if profile.ward:
            if program.target_ward == profile.ward:
                reasons.append(f"居住地が対象の区（{profile.ward}）に合致しています")
            else:
                return None  # 区不一致は除外
        else:
            # 区指定があるがプロフィールが未入力の場合
            score -= 10
            warnings.append("区単位の対象条件の確認が必要です")

    # -------------------------
    # 2. 年齢条件
    # -------------------------
    if condition and (condition.min_age is not None or condition.max_age is not None):
        if age is None:
            score -= 20
            warnings.append("年齢制限がある制度です。生年月日の登録を確認してください")
        elif condition.min_age is not None and age < condition.min_age:
            return None  # 年齢下限未満は除外
        elif condition.max_age is not None and age > condition.max_age:
            return None  # 年齢上限超過は除外
        else:
            reasons.append("年齢条件に合致しています")
    else:
        reasons.append("年齢制限のない制度です")

    # -------------------------
    # 3. 所得・税条件
    # -------------------------
    # 所得上限
    if condition and condition.max_annual_income is not None:
        if profile.annual_income_max is None:
            score -= 20
            warnings.append("所得制限がある制度です。所得情報の確認が必要です")
        elif profile.annual_income_max > condition.max_annual_income:
            return None  # 所得上限超過は除外
        else:
            # 閾値に近い場合の減点 (閾値の80%以上)
            if profile.annual_income_max >= (condition.max_annual_income * 0.8):
                score -= 15
                warnings.append("所得制限の境界線付近です。正確な所得による確認が必要です")
            else:
                reasons.append("所得条件に合致している可能性が高いです")
    else:
        reasons.append("所得制限のない制度です")

    # 非課税世帯
    if condition and condition.requires_tax_exempt is True:
        if profile.is_tax_exempt_household is True:
            reasons.append("非課税世帯の条件を満たしています")
        elif profile.is_tax_exempt_household is False:
            return None  # 非課税世帯限定で、明確に「いいえ」の場合は除外
        else:
            # 「わからない・不明」の場合
            score -= 20
            warnings.append("住民税非課税世帯であるか確認が必要です")

    # -------------------------
    # 4. 世帯・属性条件
    # -------------------------
    # 子どもの有無
    if condition and condition.requires_children is True:
        if profile.has_children:
            reasons.append("子どもがいる世帯向け条件を満たしています")
            if condition.min_children_count is not None:
                if profile.children_count < condition.min_children_count:
                    return None  # 子どもの人数不足は除外
        else:
            return None  # 子ども必須で「なし」の場合は除外

    # ひとり親
    if condition and condition.requires_single_parent is True:
        if profile.is_single_parent is True:
            reasons.append("ひとり親世帯の条件を満たしています")
        elif profile.is_single_parent is False:
            return None  # ひとり親限定で、明確に「いいえ」の場合は除外
        else:
            # 「不明・その他」の場合
            score -= 15
            warnings.append("ひとり親世帯等の対象条件の確認が必要です")

    # 性別
    if condition and condition.required_gender is not None:
        if profile.gender == condition.required_gender:
            reasons.append("性別条件に合致しています")
        elif profile.gender in ["no_answer", "other"]:
            score -= 10
            warnings.append("性別による対象制限の確認が必要です")
        else:
            return None  # 性別不一致は除外

    # 世帯主 (v2拡張)
    if condition and getattr(condition, "requires_household_head", False) is True:
        if profile.is_household_head is True:
            reasons.append("世帯主である条件を満たしています")
        elif profile.is_household_head is False:
            return None
        else:
            score -= 10
            warnings.append("世帯主であるか確認が必要です")

    # 賃貸 (v2拡張)
    if condition and getattr(condition, "requires_rent", False) is True:
        if profile.housing_status == "rented":
            reasons.append("賃貸住宅にお住まいの条件を満たしています")
        elif profile.housing_status and profile.housing_status != "rented":
            return None
        else:
            score -= 10
            warnings.append("住居形態（賃貸等）の確認が必要です")

    # -------------------------
    # 5. 就労・特別条件 (v2拡張)
    # -------------------------
    if condition:
        # 離職
        if getattr(condition, "requires_unemployed", False) is True:
            is_unemp = employment.is_unemployed if employment else None
            if is_unemp is True:
                reasons.append("離職中の方を対象とした条件を満たしています")
            elif is_unemp is False:
                return None
            else:
                score -= 20
                warnings.append("離職中であるか確認が必要です")

        # 収入減少
        if getattr(condition, "requires_income_decreased", False) is True:
            inc_dec = employment.income_decreased if employment else None
            if inc_dec is True:
                reasons.append("収入が減少している条件を満たしています")
            elif inc_dec is False:
                return None
            else:
                score -= 15
                warnings.append("収入減少の有無について確認が必要です")

        # 健康保険
        if getattr(condition, "requires_health_insurance", False) is True:
            has_ins = special.has_health_insurance if special else None
            if has_ins is True:
                reasons.append("健康保険に加入している条件を満たしています")
            elif has_ins is False:
                return None
            else:
                score -= 10
                warnings.append("健康保険の加入状況を確認してください")

        # 障害
        if getattr(condition, "requires_disability", False) is True:
            has_dis = special.has_disability if special else None
            if has_dis is True:
                reasons.append("障害をお持ちの方を対象とした条件を満たしています")
            elif has_dis is False:
                return None
            else:
                score -= 20
                warnings.append("障害の有無について確認が必要です")

    # -------------------------
    # 6. 特殊条件・人間確認 (v2拡張)
    # -------------------------
    if condition and getattr(condition, "is_extraordinary_condition", False) is True:
        score -= 50  # 特殊条件の場合は大幅にスコアを下げる
        warnings.append("災害や特殊な被害等に遭われた方向けの限定的な制度です")

    if condition and getattr(condition, "manual_check_required", False):
        score -= 20  # AIが詳細確認を推奨するものは減点
        warnings.append("詳細な対象条件は、自治体の窓口等で確認が必要です")

    # 信頼度による微調整
    if getattr(program, "confidence_level", None) == "estimated":
        score -= 5  # AI抽出データは信頼性の観点から微減点

    # 具体的な条件設定が乏しい（汎用性が高すぎる）場合の調整
    has_specific_condition = False
    if condition:
        fields_to_check = [
            "min_age", "max_age", "max_annual_income", "requires_tax_exempt",
            "requires_children", "requires_single_parent", "requires_disability",
            "requires_unemployed", "requires_rent"
        ]
        for field in fields_to_check:
            if getattr(condition, field, None) is not None:
                has_specific_condition = True
                break
    
    if not has_specific_condition:
        score -= 5  # 具体的な制限がない広報的な制度は優先度をわずかに下げる

    # -------------------------
    # 7. 最終判定の集約
    # -------------------------
    # 減点が発生している場合はステータスをダウングレード
    if warnings:
        status = "possible"

    # スコアの下限・上限補正
    final_score = max(0, min(score, 100))

    return {
        "program": program,
        "score": final_score,
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
