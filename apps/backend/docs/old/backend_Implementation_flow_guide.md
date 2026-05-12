# 支援制度マッチングアプリ：バックエンド実装イメージ補足資料

この資料は、バックエンド設計書だけでは見えにくい、**実際の処理の流れ・各フォルダの役割・コードのつながり・APIの動かし方**を理解するための補足資料である。

目的は、単にフォルダ構成を覚えることではない。

**「Next.jsからAPIが呼ばれたとき、FastAPIのどのファイルを通って、DBにアクセスし、どのようにレスポンスが返るのか」**を具体的にイメージできるようにすることである。

---

# 1. まず全体像を理解する

このバックエンドは、以下のようなレイヤード構成で考える。

```text
Frontend: Next.js
  ↓ HTTP Request
routers/       APIの入口
  ↓
schemas/       入力・出力データの型チェック
  ↓
services/      アプリ固有の処理
  ↓
repositories/  DB操作
  ↓
models/        DBテーブル定義
  ↓
SQLite (初期プロトタイプ用)
```

このアプリでは、バックエンドの中核は次の3種類の処理である。

```text
1. プロフィール保存
2. 支援制度情報の管理
3. 支援制度マッチング
```

開発を迅速に進めるため、**ユーザー認証（登録・ログイン）は含めない**構成とする。

---

# 2. フォルダ構成の再整理

基本構成は以下の通りである。

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── profile.py
│   │   ├── support_program.py
│   │   └── match_result.py
│   │
│   ├── schemas/
│   │   ├── profile.py
│   │   ├── support_program.py
│   │   └── match.py
│   │
│   ├── routers/
│   │   ├── profiles.py
│   │   ├── programs.py
│   │   └── matches.py
│   │
│   ├── services/
│   │   ├── profile_service.py
│   │   ├── program_service.py
│   │   └── matching_service.py
│   │
│   ├── repositories/
│   │   ├── profile_repository.py
│   │   └── program_repository.py
│   │
│   └── seed/
│       └── seed_programs.py
│
├── migrations/
├── tests/
├── .env
├── requirements.txt
└── README.md
```

---

# 3. 各フォルダの役割

## 3.1 main.py

`main.py` はFastAPIアプリの起動点である。

```python
# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import profiles, programs, matches

app = FastAPI(title="Support Matching API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(profiles.router)
app.include_router(programs.router)
app.include_router(matches.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

---

## 3.2 core/

### config.py

```python
# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./app.db"

    class Config:
        env_file = ".env"

settings = Settings()
```

### database.py

```python
# app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# SQLite用の設定（check_same_threadはSQLite特有）
engine = create_engine(
    settings.database_url, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 3.3 models/

### profile.py

```python
# app/models/profile.py

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from sqlalchemy.sql import func
from app.core.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    
    # 属性情報
    prefecture = Column(String, nullable=False)
    city = Column(String, nullable=False)
    ward = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    
    # 性別: 特定の性別（例：出産支援など）を対象とした制度の判定に利用
    gender = Column(String, nullable=True) 
    
    # 配偶者の有無: 配偶者控除や家族向け支援制度の判定に利用
    has_spouse = Column(Boolean, nullable=True)
    
    has_children = Column(Boolean, nullable=True)
    annual_income = Column(Integer, nullable=True)
    is_tax_exempt_household = Column(Boolean, nullable=True)
    employment_status = Column(String, nullable=True)
    is_student = Column(Boolean, nullable=True)
    is_single_parent = Column(Boolean, nullable=True)
    is_disabled = Column(Boolean, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

## 3.4 schemas/

### profile.py

```python
# app/schemas/profile.py

from pydantic import BaseModel
from typing import Optional
from datetime import date

class ProfileRequest(BaseModel):
    prefecture: str
    city: str
    ward: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    has_spouse: Optional[bool] = None
    has_children: Optional[bool] = None
    annual_income: Optional[int] = None
    is_tax_exempt_household: Optional[bool] = None
    employment_status: Optional[str] = None
    is_student: Optional[bool] = None
    is_single_parent: Optional[bool] = None
    is_disabled: Optional[bool] = None

class ProfileResponse(ProfileRequest):
    id: int

    class Config:
        from_attributes = True
```

---

# 4. 処理フロー：プロフィール登録・更新

認証なしのため、シンプルに1つのプロフィール（または最新のもの）を扱う。

## 4.1 API
`GET /profile`, `PUT /profile`

## 4.2 コード例

### routers/profiles.py

```python
# app/routers/profiles.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.profile import ProfileRequest, ProfileResponse
from app.services.profile_service import get_profile, upsert_profile

router = APIRouter(prefix="/profile", tags=["profiles"])

@router.get("", response_model=ProfileResponse)
def read_profile(db: Session = Depends(get_db)):
    return get_profile(db)

@router.put("", response_model=ProfileResponse)
def update_profile(request: ProfileRequest, db: Session = Depends(get_db)):
    return upsert_profile(db, request)
```

---

# 5. 処理フロー：支援制度一覧・詳細取得

## 5.1 services/program_service.py 実装例

```python
# app/services/program_service.py

from fastapi import HTTPException
from app.repositories import program_repository

def list_programs(db, category=None, city=None):
    return program_repository.search_programs(db, category=category, city=city)

def get_program_detail(db, program_id: int):
    program = program_repository.get_program_by_id(db, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return program
```

---

# 6. 処理フロー：マッチング処理

## 6.1 マッチングロジック (calculate_match_score)

スコア配分 (合計100点):
- 地域一致: 30点 (都道府県15, 市10, 区5)
- 年齢条件: 15点
- 所得・税条件: 25点 (所得15, 非課税10)
- 世帯・雇用条件: 30点 (雇用10, 子供10, ひとり親5, 障害5)

```python
# app/services/matching_service.py (抜粋)

def calculate_match_score(profile, program, condition):
    age = calculate_age(profile.birth_date) if profile.birth_date else None
    score = 0
    reasons = []
    warnings = []
    failed_required_conditions = []

    # 地域条件 (30点)
    if program.target_prefecture and program.target_prefecture != profile.prefecture:
        failed_required_conditions.append("対象都道府県が一致しません")
    else:
        score += 15
        if program.target_city:
            if program.target_city != profile.city:
                failed_required_conditions.append("対象市区町村が一致しません")
            else:
                score += 10
                if program.target_ward and program.target_ward != profile.ward:
                    failed_required_conditions.append("対象区が一致しません")
                else:
                    score += 5

    # 年齢条件 (15点)
    if condition.min_age is not None and age is not None and age < condition.min_age:
        failed_required_conditions.append("年齢条件(下限)を満たしていません")
    elif condition.max_age is not None and age is not None and age > condition.max_age:
        failed_required_conditions.append("年齢条件(上限)を満たしていません")
    elif condition.min_age or condition.max_age:
        if age is None: warnings.append("年齢確認が必要です")
        else: score += 15

    # 所得・税条件 (25点)
    if condition.max_annual_income is not None:
        if profile.annual_income is None: warnings.append("所得確認が必要です")
        elif profile.annual_income <= condition.max_annual_income: score += 15
        else: failed_required_conditions.append("所得制限を超えています")
    
    if condition.requires_tax_exempt:
        if profile.is_tax_exempt_household: score += 10
        else: failed_required_conditions.append("非課税世帯向けの制度です")

    # 世帯・雇用条件 (30点)
    if condition.requires_unemployed and profile.employment_status != "unemployed":
        failed_required_conditions.append("離職中の方向けの制度です")
    elif condition.requires_unemployed: score += 10

    if condition.requires_children:
        if profile.has_children: score += 10
        else: failed_required_conditions.append("子供がいる世帯向けの制度です")

    if condition.requires_single_parent:
        if profile.is_single_parent: score += 5
        else: failed_required_conditions.append("ひとり親家庭向けの制度です")

    if condition.requires_disabled:
        if profile.is_disabled: score += 5
        else: failed_required_conditions.append("障害をお持ちの方向けの制度です")

    if failed_required_conditions: return None

    status = "possible" if warnings else "eligible"
    return {
        "program_id": program.id,
        "score": score,
        "status": status,
        "reasons": reasons,
        "warnings": warnings,
    }
```

---

# 7. APIを実際に叩くコマンド例

## 7.1 プロフィール取得・更新

```bash
# 取得
curl http://localhost:8000/profile

# 更新
curl -X PUT http://localhost:8000/profile \
  -H "Content-Type: application/json" \
  -d '{
    "prefecture": "京都府",
    "city": "京都市",
    "ward": "左京区",
    "birth_date": "2003-04-01",
    "gender": "male",
    "has_spouse": false,
    "has_children": false,
    "annual_income": 1200000,
    "is_tax_exempt_household": false,
    "employment_status": "student",
    "is_student": true,
    "is_single_parent": false,
    "is_disabled": false
  }'
```

## 7.2 マッチング結果取得

```bash
curl http://localhost:8000/matches
```

---

# 8. 最終的な理解のための一文まとめ

```text
routers/ はAPIの入口。
schemas/ はデータの型チェック。
services/ はビジネスロジック（マッチング計算など）。
repositories/ はDB操作の実行。
models/ はDBテーブル定義。
core/ は共通基盤。
```
