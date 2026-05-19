# 担当B：支援制度・マッチング機能 実装詳細ドキュメント

## 1. 担当Bの役割

担当Bは、支援制度データ管理機能とマッチング機能を垂直に実装する。

具体的には、支援制度本体と制度条件をDBに保存し、プロフィール情報と照合して、対象となる可能性のある制度一覧を返すAPIを作成する。

担当範囲は以下である。

```text
- support_programs テーブル定義
- support_program_conditions テーブル定義
- 支援制度用 Pydantic schema
- 支援制度一覧取得API
- 支援制度詳細取得API
- seed データ作成
- マッチングロジック
- マッチング結果取得API
```

---

## 2. 担当Bが作るファイル

主に以下のファイルを担当する。

```text
app/models/support_program.py
app/schemas/support_program.py
app/schemas/match.py
app/repositories/program_repository.py
app/services/program_service.py
app/services/matching_service.py
app/routers/programs.py
app/routers/matches.py
app/seed/seed_programs.py
```

必要に応じて、以下の共通ファイルにも関わる。

```text
app/main.py
app/core/database.py
```

ただし、`main.py` や `database.py` は担当Aも触る可能性があるため、変更前にチーム内で確認する。

---

## 3. 担当Aとの依存関係

マッチング機能は、担当Aが作成するプロフィール機能に依存する。

担当Bは、以下のプロフィール項目を使用する想定で実装する。

```text
profile.prefecture
profile.birth_date
profile.annual_income_max
profile.children_count
profile.has_children
profile.is_single_parent
profile.is_tax_exempt_household
profile.gender
```

### 重要な前提

* `annual_income_max` は正確な年収ではなく、所得帯の上限値である。
* `is_tax_exempt_household = None` は「わからない」を意味する。
* `is_single_parent = None` は「その他」など、判定不能を意味する。
* MVPでは `city` と `ward` はプロフィール側に存在しない可能性が高い。
* そのため、初期の地域判定は都道府県中心で行う。

---

## 4. 支援制度データ設計

支援制度データは、以下の2つに分けて保存する。

```text
support_programs
support_program_conditions
```

### 4.1 support_programs

制度そのものの情報を保存する。

例：

```text
住居確保給付金
子育て世帯生活支援特別給付金
就学援助制度
```

### 4.2 support_program_conditions

制度の対象条件を、機械的に判定しやすい形で保存する。

例：

```text
年齢上限
所得上限
子どもの有無
ひとり親かどうか
非課税世帯かどうか
対象性別
```

---

## 5. DBテーブル定義

## 5.1 support_programs テーブル

`app/models/support_program.py` に `SupportProgram` モデルを定義する。

```python
# app/models/support_program.py

from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SupportProgram(Base):
    __tablename__ = "support_programs"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    benefit = Column(Text, nullable=True)
    category = Column(String, nullable=True)

    target_prefecture = Column(String, nullable=True)
    target_city = Column(String, nullable=True)
    target_ward = Column(String, nullable=True)

    application_url = Column(Text, nullable=True)
    deadline = Column(Date, nullable=True)
    required_documents = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    condition = relationship(
        "SupportProgramCondition",
        back_populates="program",
        uselist=False,
        cascade="all, delete-orphan",
    )
```

---

## 5.2 support_program_conditions テーブル

同じく `app/models/support_program.py` に `SupportProgramCondition` モデルを定義する。

```python
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


class SupportProgramCondition(Base):
    __tablename__ = "support_program_conditions"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("support_programs.id"), nullable=False)

    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)

    max_annual_income = Column(Integer, nullable=True)

    requires_tax_exempt = Column(Boolean, nullable=True)
    requires_children = Column(Boolean, nullable=True)
    min_children_count = Column(Integer, nullable=True)
    requires_single_parent = Column(Boolean, nullable=True)

    required_gender = Column(String, nullable=True)

    condition_description = Column(Text, nullable=True)

    program = relationship("SupportProgram", back_populates="condition")
```

### MVPでは入れない条件

既存設計には以下の条件があったが、プロフィール入力仕様に存在しないため、MVPでは原則使わない。

```text
requires_student
requires_unemployed
requires_disabled
```

将来的にプロフィール画面に項目を追加する場合は、この条件も復活させる。

---

## 6. Pydantic schema

## 6.1 支援制度schema

`app/schemas/support_program.py` に定義する。

```python
# app/schemas/support_program.py

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


class ProgramDetailResponse(ProgramListItemResponse):
    requiredDocuments: Optional[str] = None
    sourceUrl: Optional[str] = None
    condition: Optional[ProgramConditionResponse] = None
```

---

## 6.2 マッチングschema

`app/schemas/match.py` に定義する。

```python
# app/schemas/match.py

from pydantic import BaseModel
from typing import Optional, List
from app.schemas.support_program import ProgramListItemResponse


class MatchResultResponse(BaseModel):
    program: ProgramListItemResponse
    score: int
    status: str
    reasons: List[str]
    warnings: List[str]
```

### status の値

```text
eligible: 入力情報上、条件を満たしている可能性が高い
possible: 一部追加確認が必要だが、対象となる可能性がある
```

MVPでは、明確に対象外の制度はレスポンスに含めない。

---

## 7. Repository層

`app/repositories/program_repository.py` にDB操作を書く。

```python
# app/repositories/program_repository.py

from sqlalchemy.orm import Session, joinedload
from app.models.support_program import SupportProgram


def list_programs(db: Session, category: str | None = None, prefecture: str | None = None):
    query = db.query(SupportProgram).filter(SupportProgram.is_active == True)

    if category:
        query = query.filter(SupportProgram.category == category)

    if prefecture:
        query = query.filter(
            (SupportProgram.target_prefecture == prefecture)
            | (SupportProgram.target_prefecture == None)
        )

    return query.order_by(SupportProgram.id.asc()).all()


def get_program_by_id(db: Session, program_id: int):
    return (
        db.query(SupportProgram)
        .options(joinedload(SupportProgram.condition))
        .filter(SupportProgram.id == program_id)
        .filter(SupportProgram.is_active == True)
        .first()
    )


def list_programs_with_conditions(db: Session):
    return (
        db.query(SupportProgram)
        .options(joinedload(SupportProgram.condition))
        .filter(SupportProgram.is_active == True)
        .order_by(SupportProgram.id.asc())
        .all()
    )
```

---

## 8. Service層：支援制度一覧・詳細

`app/services/program_service.py` に支援制度取得処理を書く。

```python
# app/services/program_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories import program_repository


def get_programs(db: Session, category: str | None = None, prefecture: str | None = None):
    return program_repository.list_programs(
        db,
        category=category,
        prefecture=prefecture,
    )


def get_program_detail(db: Session, program_id: int):
    program = program_repository.get_program_by_id(db, program_id)
    if program is None:
        raise HTTPException(status_code=404, detail="Program not found")
    return program
```

---

## 9. Router層：支援制度API

`app/routers/programs.py` にAPIを書く。

```python
# app/routers/programs.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.program_service import get_programs, get_program_detail


router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("")
def read_programs(
    category: str | None = Query(default=None),
    prefecture: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return get_programs(db, category=category, prefecture=prefecture)


@router.get("/{program_id}")
def read_program_detail(program_id: int, db: Session = Depends(get_db)):
    return get_program_detail(db, program_id)
```

---

## 10. seed データ作成

初期段階では、制度データの自動収集は行わない。

担当Bは、動作確認用に数件の支援制度データを seed として登録する。

`app/seed/seed_programs.py` を作成する。

```python
# app/seed/seed_programs.py

from app.core.database import SessionLocal
from app.models.support_program import SupportProgram, SupportProgramCondition


def seed_programs():
    db = SessionLocal()

    try:
        existing = db.query(SupportProgram).first()
        if existing:
            print("Seed data already exists")
            return

        programs = [
            SupportProgram(
                title="住居確保給付金",
                provider="京都市",
                summary="離職等により住居を失うおそれがある方に家賃相当額を支給する制度です。",
                benefit="家賃相当額を一定期間支給",
                category="housing",
                target_prefecture="京都府",
                target_city="京都市",
                target_ward=None,
                application_url="https://example.com/housing",
                source_url="https://example.com/source/housing",
                is_active=True,
                condition=SupportProgramCondition(
                    max_annual_income=4_000_000,
                    condition_description="収入が一定額以下であること等",
                ),
            ),
            SupportProgram(
                title="子育て世帯生活支援特別給付金",
                provider="国・自治体",
                summary="子育て世帯の生活を支援するための給付金です。",
                benefit="対象児童1人あたり一定額を支給",
                category="childcare",
                target_prefecture=None,
                application_url="https://example.com/childcare",
                source_url="https://example.com/source/childcare",
                is_active=True,
                condition=SupportProgramCondition(
                    requires_children=True,
                    min_children_count=1,
                    condition_description="子どもがいる世帯が対象です。",
                ),
            ),
            SupportProgram(
                title="低所得世帯向け給付金",
                provider="自治体",
                summary="住民税非課税世帯等を対象とした給付金です。",
                benefit="一定額を支給",
                category="low_income",
                target_prefecture=None,
                application_url="https://example.com/low-income",
                source_url="https://example.com/source/low-income",
                is_active=True,
                condition=SupportProgramCondition(
                    requires_tax_exempt=True,
                    condition_description="住民税非課税世帯等が対象です。",
                ),
            ),
        ]

        db.add_all(programs)
        db.commit()
        print("Seed data inserted")

    finally:
        db.close()


if __name__ == "__main__":
    seed_programs()
```

### 注意

上記URLは仮である。

実際にアプリとして見せる場合は、公式サイトのURLに置き換える。

---

## 11. マッチングロジック

`app/services/matching_service.py` に実装する。

### 11.1 基本方針

マッチングでは、以下を返す。

```text
program: 制度情報
score: マッチ度スコア
status: eligible または possible
reasons: 合致理由
warnings: 追加確認が必要な項目
```

明確に対象外の制度は `None` を返し、最終レスポンスから除外する。

---

## 11.2 年齢計算

```python
# app/services/matching_service.py

from datetime import date


def calculate_age(birth_date: date, today: date | None = None) -> int:
    if today is None:
        today = date.today()

    age = today.year - birth_date.year

    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return age
```

---

## 11.3 スコア配分

MVPでは、以下を目安にする。

```text
地域一致: 30点
年齢条件: 20点
所得・税条件: 30点
世帯・属性条件: 20点
```

### 注意

スコアは厳密な法的判定ではなく、ユーザーに候補を並べて提示するための目安である。

---

## 11.4 マッチング関数

```python
# app/services/matching_service.py


def calculate_match_score(profile, program, condition):
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

    # city / ward はMVPのプロフィールに存在しない可能性があるため、ここでは厳密判定しない
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

    if condition and condition.max_annual_income is not None:
        if profile.annual_income_max is None:
            warnings.append("所得条件の確認が必要です")
        elif profile.annual_income_max <= condition.max_annual_income:
            income_tax_score += 15
            reasons.append("所得条件を満たしている可能性があります")
        else:
            # 所得帯の上限で比較しているため、完全に断定しすぎない
            failed_required_conditions.append("所得条件を満たさない可能性があります")
    else:
        income_tax_score += 15
        reasons.append("所得条件の指定がありません")

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

    if condition and condition.requires_children is True:
        if profile.has_children:
            household_score += 10
            reasons.append("子どもがいる世帯向け条件を満たしています")
        else:
            failed_required_conditions.append("子どもがいる世帯向けの制度です")
    else:
        household_score += 10
        reasons.append("子どもの有無に関する条件指定がありません")

    if condition and condition.min_children_count is not None:
        if profile.children_count >= condition.min_children_count:
            reasons.append("子どもの人数条件を満たしています")
        else:
            failed_required_conditions.append("子どもの人数条件を満たしていません")

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
    # 5. 対象外処理
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
```

---

## 12. マッチング一覧取得処理

同じく `app/services/matching_service.py` に実装する。

```python
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories import profile_repository, program_repository


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

    results.sort(key=lambda x: x["score"], reverse=True)

    return results
```

---

## 13. Router層：マッチングAPI

`app/routers/matches.py` にAPIを書く。

```python
# app/routers/matches.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.matching_service import get_matches


router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("")
def read_matches(db: Session = Depends(get_db)):
    return get_matches(db)
```

---

## 14. main.pyへのルーター登録

`app/main.py` に、担当Bが作成したルーターを登録する。

```python
from app.routers import profiles, programs, matches

app.include_router(profiles.router)
app.include_router(programs.router)
app.include_router(matches.router)
```

`profiles` は担当Aのファイルであるため、importの衝突に注意する。

---

## 15. 動作確認

## 15.1 支援制度一覧取得

```bash
curl http://localhost:8000/programs
```

期待レスポンス例：

```json
[
  {
    "id": 1,
    "title": "住居確保給付金",
    "provider": "京都市",
    "summary": "離職等により住居を失うおそれがある方に家賃相当額を支給する制度です。",
    "benefit": "家賃相当額を一定期間支給",
    "category": "housing",
    "target_prefecture": "京都府",
    "target_city": "京都市",
    "target_ward": null,
    "application_url": "https://example.com/housing",
    "deadline": null
  }
]
```

---

## 15.2 支援制度詳細取得

```bash
curl http://localhost:8000/programs/1
```

期待レスポンス例：

```json
{
  "id": 1,
  "title": "住居確保給付金",
  "provider": "京都市",
  "summary": "離職等により住居を失うおそれがある方に家賃相当額を支給する制度です。",
  "benefit": "家賃相当額を一定期間支給",
  "category": "housing",
  "target_prefecture": "京都府",
  "condition": {
    "max_annual_income": 4000000,
    "condition_description": "収入が一定額以下であること等"
  }
}
```

---

## 15.3 マッチング結果取得

事前に担当Aの `PUT /profile` でプロフィールを登録しておく。

```bash
curl http://localhost:8000/matches
```

期待レスポンス例：

```json
[
  {
    "program": {
      "id": 1,
      "title": "住居確保給付金",
      "provider": "京都市",
      "summary": "離職等により住居を失うおそれがある方に家賃相当額を支給する制度です。",
      "benefit": "家賃相当額を一定期間支給",
      "category": "housing",
      "application_url": "https://example.com/housing"
    },
    "score": 85,
    "status": "possible",
    "reasons": [
      "居住地が対象都道府県に含まれています",
      "年齢条件の指定がありません",
      "所得条件を満たしている可能性があります"
    ],
    "warnings": [
      "市区町村単位の対象条件は公式情報の確認が必要です"
    ]
  }
]
```

---

## 16. エラーケース

### 16.1 存在しない制度ID

```bash
curl http://localhost:8000/programs/999
```

期待レスポンス：

```json
{
  "detail": "Program not found"
}
```

HTTPステータスは `404`。

### 16.2 プロフィール未登録でマッチング

```bash
curl http://localhost:8000/matches
```

期待レスポンス：

```json
{
  "detail": "Profile not found"
}
```

HTTPステータスは `404`。

---

## 17. 実装チェックリスト

担当Bの完了条件は以下である。

```text
[ ] app/models/support_program.py を作成した
[ ] SupportProgram モデルを定義した
[ ] SupportProgramCondition モデルを定義した
[ ] app/schemas/support_program.py を作成した
[ ] app/schemas/match.py を作成した
[ ] app/repositories/program_repository.py を作成した
[ ] app/services/program_service.py を作成した
[ ] app/services/matching_service.py を作成した
[ ] app/routers/programs.py を作成した
[ ] app/routers/matches.py を作成した
[ ] app/seed/seed_programs.py を作成した
[ ] seed データを投入できる
[ ] GET /programs が動作する
[ ] GET /programs/{program_id} が動作する
[ ] GET /matches が動作する
[ ] マッチング結果がスコア降順で返る
[ ] reasons が返る
[ ] warnings が返る
[ ] プロフィール未登録時に 404 を返す
```

---

## 18. 担当Aに確認すべきこと

実装前または実装中に、担当Aと以下を確認する。

```text
[ ] profile_repository.get_current_profile(db) が使えるか
[ ] UserProfile に birth_date があるか
[ ] UserProfile に prefecture があるか
[ ] UserProfile に annual_income_max があるか
[ ] UserProfile に children_count があるか
[ ] UserProfile に has_children があるか
[ ] UserProfile に is_single_parent があるか
[ ] UserProfile に is_tax_exempt_household があるか
[ ] UserProfile に gender があるか
```

特に、マッチング処理はプロフィール項目名に依存するため、項目名が変わった場合はすぐに共有する。

---

## 19. 注意点

### 19.1 マッチングは法的判定ではない

このアプリのマッチング結果は、あくまで「対象となる可能性のある制度」を提示するものである。

そのため、レスポンスや画面上では以下のような表現が望ましい。

```text
対象となる可能性があります
条件に該当する可能性があります
詳細は公式情報をご確認ください
```

逆に、以下のような断定表現は避ける。

```text
必ず受給できます
申請すれば必ず通ります
あなたは対象です
```

### 19.2 所得帯による判定は不確実

プロフィールでは正確な年収ではなく、所得帯を扱う。

例えば、ユーザーが「200万円〜400万円未満」を選んだ場合、内部では `annual_income_max = 4000000` となる。

制度の所得上限が300万円の場合、実際の年収が250万円なら対象だが、350万円なら対象外になる。

このような場合は、明確な対象外としすぎず、`warnings` に「正確な所得確認が必要です」と出す設計も検討する。

### 19.3 地域判定はMVPでは粗い

フロント入力仕様には `city` や `ward` が存在しない。

そのため、MVPでは都道府県単位の判定を中心にする。

制度側に `target_city` や `target_ward` がある場合は、対象外と断定せず、`warnings` に追加する。

### 19.4 seed データの情報源

実際の支援制度を入れる場合は、公式サイトの情報源URLを必ず保存する。

```text
source_url
application_url
```

初期デモでは仮URLでも動作確認はできるが、発表や提出で見せる場合は公式情報に置き換える。

---

## 20. 追加実装候補

MVP完成後、余裕があれば以下を検討する。

```text
- カテゴリ検索
- 都道府県検索
- 支援制度登録API
- 支援制度更新API
- 対象外理由も返すモード
- マッチング条件の重み調整
- 市区町村入力への対応
- 制度データのCSV投入
```

ただし、最初から作り込みすぎると完成しにくくなるため、まずは以下を優先する。

```text
プロフィールを保存する
制度一覧を出す
プロフィールに合いそうな制度を返す
```
