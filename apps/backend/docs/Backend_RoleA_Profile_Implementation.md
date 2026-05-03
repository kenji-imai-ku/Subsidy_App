# 担当A：プロフィール機能 実装詳細ドキュメント

## 1. 担当Aの役割

担当Aは、プロフィール機能を垂直に実装する。

具体的には、フロントエンドのプロフィール入力画面から送信されるデータを受け取り、バックエンド側でバリデーション・変換を行い、SQLiteに保存できる状態にする。

担当範囲は以下である。

```text
- user_profiles テーブル定義
- プロフィール用 Pydantic schema
- フロント入力値から内部形式への変換処理
- プロフィール保存・更新処理
- プロフィール取得処理
- GET /profile API
- PUT /profile API
```

---

## 2. 担当Aが作るファイル

主に以下のファイルを担当する。

```text
app/models/profile.py
app/schemas/profile.py
app/repositories/profile_repository.py
app/services/profile_service.py
app/routers/profiles.py
```

必要に応じて、以下の共通ファイルにも関わる。

```text
app/main.py
app/core/database.py
```

ただし、`main.py` や `database.py` は担当Bも触る可能性があるため、変更前にチーム内で確認する。

---

## 3. フロントエンドから送られるデータ

現時点で、フロントエンドからは以下の形式で送信される想定である。

```ts
type FormData = {
  name: string;
  prefecture: string;
  birthYear: string;
  birthMonth: string;
  birthDay: string;
  householdIncome: string;
  familyType: string;
  childrenCount: string;
  gender: string;
  taxExempt: string;
};
```

### 必須項目

```text
name
prefecture
birthYear
birthMonth
birthDay
householdIncome
familyType
gender
taxExempt
```

### 任意項目

```text
childrenCount
```

`childrenCount` は未入力の場合、バックエンド側で `0` として扱う。

---

## 4. バックエンド側の方針

フロントエンドの入力形式をそのままDBに保存するのではなく、バックエンド側でマッチングしやすい形に変換して保存する。

### 4.1 生年月日

フロントエンドからは以下の3つが送られる。

```text
birthYear
birthMonth
birthDay
```

バックエンドでは、この3つを結合して `birth_date` に変換する。

例：

```json
{
  "birthYear": "2003",
  "birthMonth": "4",
  "birthDay": "1"
}
```

内部保存：

```text
birth_date = 2003-04-01
```

### 4.2 子どもの人数

フロントエンドからは `childrenCount` が文字列で送られる可能性がある。

バックエンドでは整数に変換する。

```text
childrenCount: "2" → children_count: 2
```

未入力、空文字、null の場合は `0` とする。

また、以下の派生値を作る。

```text
has_children = children_count > 0
```

### 4.3 所得帯

フロントエンドからは、以下のいずれかのラベルが送られる。

```text
200万円未満
200万円〜400万円未満
400万円〜600万円未満
600万円〜800万円未満
800万円〜1,000万円未満
1,000万円以上
```

DBには元のラベル `household_income_label` と、マッチング用の `annual_income_max` を保存する。

| householdIncome | annual_income_max |
| --------------- | ----------------: |
| 200万円未満         |           2000000 |
| 200万円〜400万円未満   |           4000000 |
| 400万円〜600万円未満   |           6000000 |
| 600万円〜800万円未満   |           8000000 |
| 800万円〜1,000万円未満 |          10000000 |
| 1,000万円以上       |              null |

`1,000万円以上` は上限値がないため `null` とする。

### 4.4 世帯区分

フロントエンドからは以下のいずれかが送られる。

```text
独身
配偶者あり
ひとり親
その他
```

DBには元の値 `family_type` を保存し、加えて判定用の値を保存する。

| familyType | has_spouse | is_single_parent |
| ---------- | ---------: | ---------------: |
| 独身         |      false |            false |
| 配偶者あり      |       true |            false |
| ひとり親       |      false |             true |
| その他        |       null |             null |

### 4.5 性別

フロントエンドからは以下のいずれかが送られる。

```text
男性
女性
その他
回答しない
```

内部では以下のコードに変換して保存する。

| フロント入力 | 内部値       |
| ------ | --------- |
| 男性     | male      |
| 女性     | female    |
| その他    | other     |
| 回答しない  | no_answer |

レスポンスでは、フロントエンドで再表示しやすいように日本語ラベルで返してもよい。

### 4.6 非課税世帯

フロントエンドからは以下のいずれかが送られる。

```text
はい
いいえ
わからない
```

内部では以下のように変換する。

| taxExempt | is_tax_exempt_household |
| --------- | ----------------------: |
| はい        |                    true |
| いいえ       |                   false |
| わからない     |                    null |

`null` は、マッチング時に「追加確認が必要」として扱う。

---

## 5. DBテーブル定義

`app/models/profile.py` に `UserProfile` モデルを定義する。

```python
# app/models/profile.py

from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime
from sqlalchemy.sql import func
from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    prefecture = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)

    gender = Column(String, nullable=False)

    household_income_label = Column(String, nullable=False)
    annual_income_max = Column(Integer, nullable=True)

    family_type = Column(String, nullable=False)
    has_spouse = Column(Boolean, nullable=True)

    children_count = Column(Integer, nullable=False, default=0)
    has_children = Column(Boolean, nullable=False, default=False)
    is_single_parent = Column(Boolean, nullable=True)

    is_tax_exempt_household = Column(Boolean, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 注意

既存設計にあった以下の項目は、フロント入力仕様にないためMVPでは実装しない。

```text
city
ward
employment_status
is_student
is_disabled
```

将来的に必要になった場合は追加する。

---

## 6. Pydantic schema

`app/schemas/profile.py` にリクエスト・レスポンスの型を定義する。

### 6.1 リクエストschema

```python
# app/schemas/profile.py

from pydantic import BaseModel, Field
from typing import Optional


class ProfileRequest(BaseModel):
    name: str
    prefecture: str
    birthYear: str
    birthMonth: str
    birthDay: str
    householdIncome: str
    familyType: str
    childrenCount: Optional[str] = "0"
    gender: str
    taxExempt: str
```

### 6.2 レスポンスschema

```python
from datetime import date
from pydantic import BaseModel
from typing import Optional


class ProfileResponse(BaseModel):
    id: int
    name: str
    prefecture: str
    birthDate: date
    gender: str
    householdIncome: str
    familyType: str
    childrenCount: int
    taxExempt: str

    class Config:
        from_attributes = True
```

### 6.3 内部変換後のデータ型

必須ではないが、サービス層で扱いやすくするため、内部変換後の型を用意してもよい。

```python
from datetime import date
from pydantic import BaseModel
from typing import Optional


class ProfileInternalData(BaseModel):
    name: str
    prefecture: str
    birth_date: date
    gender: str
    household_income_label: str
    annual_income_max: Optional[int]
    family_type: str
    has_spouse: Optional[bool]
    children_count: int
    has_children: bool
    is_single_parent: Optional[bool]
    is_tax_exempt_household: Optional[bool]
```

---

## 7. 入力値変換処理

`app/services/profile_service.py` に、フロント入力値を内部形式に変換する関数を作る。

```python
# app/services/profile_service.py

from datetime import date
from fastapi import HTTPException
from app.schemas.profile import ProfileRequest


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
```

---

## 8. Repository層

`app/repositories/profile_repository.py` にDB操作を書く。

認証なしのMVPでは、最新の1件、またはIDが最小の1件をプロフィールとして扱う。

```python
# app/repositories/profile_repository.py

from sqlalchemy.orm import Session
from app.models.profile import UserProfile


def get_current_profile(db: Session) -> UserProfile | None:
    return db.query(UserProfile).order_by(UserProfile.id.desc()).first()


def create_profile(db: Session, data: dict) -> UserProfile:
    profile = UserProfile(**data)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(db: Session, profile: UserProfile, data: dict) -> UserProfile:
    for key, value in data.items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(profile)
    return profile
```

---

## 9. Service層

`app/services/profile_service.py` に、APIから呼ばれるプロフィール処理を書く。

```python
# app/services/profile_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.schemas.profile import ProfileRequest
from app.repositories import profile_repository


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
```

---

## 10. Response変換

DB上の値とフロントに返したい値が異なるため、レスポンス用に変換する関数を作るとよい。

```python
# app/services/profile_service.py

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
```

`None` を辞書キーに使う場合、`dict.get(None)` が正しく動く点に注意する。

---

## 11. Router層

`app/routers/profiles.py` にAPIエンドポイントを書く。

```python
# app/routers/profiles.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.profile import ProfileRequest, ProfileResponse
from app.services.profile_service import get_profile, upsert_profile, to_profile_response


router = APIRouter(prefix="/profile", tags=["profiles"])


@router.get("", response_model=ProfileResponse)
def read_profile(db: Session = Depends(get_db)):
    profile = get_profile(db)
    return to_profile_response(profile)


@router.put("", response_model=ProfileResponse)
def update_profile(request: ProfileRequest, db: Session = Depends(get_db)):
    profile = upsert_profile(db, request)
    return to_profile_response(profile)
```

---

## 12. main.pyへのルーター登録

`app/main.py` にプロフィールルーターを登録する。

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import profiles

app = FastAPI(title="Support Matching API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
```

担当Bが `programs` や `matches` を追加するため、`main.py` は競合しやすい。

実装時は、以下のように最終的にまとめる。

```python
from app.routers import profiles, programs, matches

app.include_router(profiles.router)
app.include_router(programs.router)
app.include_router(matches.router)
```

---

## 13. 動作確認

### 13.1 ヘルスチェック

```bash
curl http://localhost:8000/health
```

期待レスポンス：

```json
{
  "status": "ok"
}
```

### 13.2 プロフィール登録・更新

```bash
curl -X PUT http://localhost:8000/profile \
  -H "Content-Type: application/json" \
  -d '{
    "name": "松岡拓志",
    "prefecture": "京都府",
    "birthYear": "2003",
    "birthMonth": "4",
    "birthDay": "1",
    "householdIncome": "200万円〜400万円未満",
    "familyType": "独身",
    "childrenCount": "0",
    "gender": "男性",
    "taxExempt": "いいえ"
  }'
```

期待レスポンス：

```json
{
  "id": 1,
  "name": "松岡拓志",
  "prefecture": "京都府",
  "birthDate": "2003-04-01",
  "gender": "男性",
  "householdIncome": "200万円〜400万円未満",
  "familyType": "独身",
  "childrenCount": 0,
  "taxExempt": "いいえ"
}
```

### 13.3 プロフィール取得

```bash
curl http://localhost:8000/profile
```

---

## 14. エラーケース

最低限、以下のケースを確認する。

### 14.1 存在しないプロフィールを取得

プロフィール未登録の状態で以下を実行する。

```bash
curl http://localhost:8000/profile
```

期待レスポンス：

```json
{
  "detail": "Profile not found"
}
```

HTTPステータスは `404`。

### 14.2 不正な日付

```json
{
  "birthYear": "2003",
  "birthMonth": "2",
  "birthDay": "31"
}
```

期待レスポンス：

```json
{
  "detail": "Invalid birth date"
}
```

HTTPステータスは `422`。

### 14.3 子どもの人数が負数

```json
{
  "childrenCount": "-1"
}
```

期待レスポンス：

```json
{
  "detail": "childrenCount must be 0 or more"
}
```

HTTPステータスは `422`。

---

## 15. 担当Bへ共有すべき仕様

担当Bのマッチング処理は、担当Aが保存する以下の項目に依存する。

```text
birth_date
prefecture
annual_income_max
has_children
children_count
is_single_parent
is_tax_exempt_household
gender
```

特に重要なのは以下である。

### 15.1 annual_income_max の意味

`annual_income_max` は、ユーザーの正確な年収ではなく、所得帯の上限値である。

例：

```text
200万円〜400万円未満 → annual_income_max = 4000000
```

そのため、制度条件が `max_annual_income = 3000000` の場合、本当に対象外とは断定できない。

この場合は、マッチング側で `warnings` に「正確な所得確認が必要です」と出す設計が望ましい。

### 15.2 taxExempt の `null`

`is_tax_exempt_household = null` は、「わからない」を意味する。

対象外ではなく、追加確認が必要な状態として扱う。

### 15.3 familyType の `その他`

`familyType = その他` の場合、`has_spouse` と `is_single_parent` は `null` になる。

この場合も対象外と断定せず、必要に応じて `warnings` に追加する。

---

## 16. 実装チェックリスト

担当Aの完了条件は以下である。

```text
[ ] app/models/profile.py を作成した
[ ] user_profiles テーブルを定義した
[ ] app/schemas/profile.py を作成した
[ ] ProfileRequest を定義した
[ ] ProfileResponse を定義した
[ ] フロント入力値から内部値への変換処理を実装した
[ ] childrenCount を int に変換できる
[ ] birthYear/month/day を birth_date に変換できる
[ ] householdIncome を annual_income_max に変換できる
[ ] familyType から has_spouse / is_single_parent を作れる
[ ] taxExempt を true / false / null に変換できる
[ ] GET /profile を実装した
[ ] PUT /profile を実装した
[ ] curl で登録・取得確認をした
[ ] 担当Bにプロフィール項目の仕様を共有した
```

---

## 17. 注意点

### 17.1 フロント入力名とDBカラム名を混同しない

フロント入力：

```text
birthYear
householdIncome
familyType
taxExempt
```

DB保存：

```text
birth_date
household_income_label
annual_income_max
family_type
is_tax_exempt_household
```

APIリクエストではフロントに合わせる。

DBではマッチングしやすい形にする。

### 17.2 MVPでは市区町村を扱わない

既存設計では `city` や `ward` があったが、フロント入力仕様には存在しない。

そのため、MVPでは都道府県のみで地域マッチングを行う。

将来的に精度を上げる場合は、フロント側に市区町村入力を追加する。

### 17.3 プロフィールは1件扱いでよい

認証なしのため、本格的なユーザー管理は行わない。

MVPでは、最新のプロフィール1件を使う。

ただし、将来的に複数ユーザー対応する場合は、`user_id` や認証機能を追加する必要がある。
