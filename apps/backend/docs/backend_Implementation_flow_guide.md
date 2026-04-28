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
PostgreSQL
```

ただし、実際には `schemas/` は処理の途中に独立して呼び出すというより、`routers/` の引数やレスポンス型として使われる。

つまり、実際のイメージは以下に近い。

```text
Next.js
  ↓
routers/ がAPIリクエストを受け取る
  ↓
schemas/ によってリクエストJSONが検証される
  ↓
routers/ が services/ の関数を呼ぶ
  ↓
services/ が必要な処理を組み立てる
  ↓
repositories/ がDBを読み書きする
  ↓
models/ を通じてDBテーブルにアクセスする
  ↓
services/ が結果を整形する
  ↓
schemas/ の形に従ってレスポンスが返る
  ↓
Next.js が画面表示する
```

このアプリでは、バックエンドの中核は次の4種類の処理である。

```text
1. アカウント登録
2. ログイン・認証
3. プロフィール保存
4. 支援制度マッチング
```

---

# 2. フォルダ構成の再整理

基本構成は以下の通りである。

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── support_program.py
│   │   └── match_result.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── profile.py
│   │   ├── support_program.py
│   │   └── match.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── profiles.py
│   │   ├── programs.py
│   │   └── matches.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── profile_service.py
│   │   ├── program_service.py
│   │   └── matching_service.py
│   │
│   ├── repositories/
│   │   ├── user_repository.py
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

この資料では、それぞれを「処理の流れ」の中で理解する。

---

# 3. 各フォルダの役割

## 3.1 main.py

`main.py` はFastAPIアプリの起動点である。

ここで行うことは主に以下である。

```text
- FastAPIアプリの作成
- CORS設定
- routerの登録
- health check APIの定義
```

例：

```python
# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, profiles, programs, matches

app = FastAPI(title="Support Matching API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(programs.router)
app.include_router(matches.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
```

ここで `app.include_router(auth.router)` と書くことで、`routers/auth.py` に定義したAPIが使えるようになる。

---

## 3.2 core/

`core/` は、アプリ全体で共通して使う基盤処理を置く場所である。

アプリ固有の機能を書く場所ではない。

```text
core/
├── config.py      環境変数・設定値
├── database.py    DB接続設定
└── security.py    パスワードハッシュ化・JWT処理
```

### config.py

`.env` からDB接続URLやJWT秘密鍵などを読み込む。

```python
# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
```

`.env` の例：

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/support_app
SECRET_KEY=your-secret-key
```

---

### database.py

DB接続とSQLAlchemyの基本設定を書く。

```python
# app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

`get_db()` は、API処理中にDBセッションを使うための関数である。

例えば `routers/auth.py` などで以下のように使う。

```python
db: Session = Depends(get_db)
```

---

### security.py

認証・認可に関係する処理を置く。

主な役割は以下である。

```text
- パスワードをハッシュ化する
- 入力されたパスワードが正しいか検証する
- JWTアクセストークンを作成する
- JWTからログイン中ユーザーを取得する
```

例：

```python
# app/core/security.py

from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.repositories.user_repository import get_user_by_id

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception

    return user
```

この `get_current_user()` は、ログインが必要なAPIで使う。

例：

```python
current_user = Depends(get_current_user)
```

---

## 3.3 models/

`models/` はDBテーブルの定義を書く場所である。

ここには「DB操作の関数」は基本的に書かない。

```text
models/
├── user.py              usersテーブル
├── profile.py           user_profilesテーブル
├── support_program.py   support_programs, support_program_conditionsテーブル
└── match_result.py      match_resultsテーブルを使う場合
```

### user.py

```python
# app/models/user.py

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

### profile.py

```python
# app/models/profile.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date
from sqlalchemy.sql import func
from app.core.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    prefecture = Column(String, nullable=False)
    city = Column(String, nullable=False)
    ward = Column(String, nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    is_single = Column(Boolean, nullable=True)
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

### support_program.py

```python
# app/models/support_program.py

from sqlalchemy import Column, Integer, String, Text, Boolean, Date, ForeignKey, DateTime
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
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    condition = relationship("SupportProgramCondition", back_populates="program", uselist=False)

class SupportProgramCondition(Base):
    __tablename__ = "support_program_conditions"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("support_programs.id"), unique=True, nullable=False)

    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    max_annual_income = Column(Integer, nullable=True)
    requires_tax_exempt = Column(Boolean, nullable=True)
    min_household_size = Column(Integer, nullable=True)

    requires_children = Column(Boolean, nullable=True)
    requires_student = Column(Boolean, nullable=True)
    requires_unemployed = Column(Boolean, nullable=True)
    requires_single_parent = Column(Boolean, nullable=True)
    requires_disabled = Column(Boolean, nullable=True)

    condition_description = Column(Text, nullable=True)

    program = relationship("SupportProgram", back_populates="condition")
```

---

## 3.4 schemas/

`schemas/` は、APIで受け取るJSON、返すJSONの形を定義する場所である。

DBテーブル定義である `models/` とは別物である。

```text
schemas/
├── auth.py             登録・ログイン用
├── profile.py          プロフィール用
├── support_program.py  制度情報用
└── match.py            マッチ結果用
```

### auth.py

```python
# app/schemas/auth.py

from pydantic import BaseModel, EmailStr

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
```

`UserResponse` には `hashed_password` を含めない。

これにより、DBにはパスワードハッシュを持ちながら、APIレスポンスでは返さないようにできる。

---

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
    is_single: Optional[bool] = None
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
    user_id: int

    class Config:
        from_attributes = True
```

---

### match.py

```python
# app/schemas/match.py

from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class MatchResultResponse(BaseModel):
    program_id: int
    title: str
    provider: str
    summary: str
    benefit: Optional[str] = None
    category: Optional[str] = None
    score: int
    status: str
    reasons: List[str]
    warnings: List[str]
    deadline: Optional[date] = None
    application_url: Optional[str] = None
```

---

## 3.5 routers/

`routers/` はAPIの入口である。

ここでは、URLと処理を対応させる。

```text
routers/
├── auth.py       /auth/register, /auth/login
├── profiles.py   /me/profile
├── programs.py   /programs, /programs/{program_id}
└── matches.py    /me/matches
```

`routers/` に複雑な処理を書きすぎないことが重要である。

`routers/` は以下に集中する。

```text
- APIパスを定義する
- リクエストを受け取る
- ログインユーザーを取得する
- serviceを呼ぶ
- 結果を返す
```

---

## 3.6 services/

`services/` はアプリ固有の処理を書く場所である。

このアプリでは、特に `matching_service.py` が中核になる。

```text
services/
├── auth_service.py       登録・ログイン処理
├── profile_service.py    プロフィール保存・更新処理
├── program_service.py    制度情報取得処理
└── matching_service.py   マッチング処理
```

`services/` では、必要に応じて複数の `repository` を呼ぶ。

例えばマッチングでは、

```text
profile_repository からユーザー情報を取得
program_repository から制度情報を取得
matching_service で照合
```

という流れになる。

---

## 3.7 repositories/

`repositories/` はDB操作を書く場所である。

```text
repositories/
├── user_repository.py       ユーザー検索・作成
├── profile_repository.py    プロフィール取得・保存
└── program_repository.py    制度情報取得
```

ここでは、SQLAlchemyを使ってDBを読み書きする。

```text
models/ = テーブル定義
repositories/ = そのテーブルを使ったDB操作
```

という関係である。

---

# 4. 処理フロー1：アカウント登録

アカウント登録は、ユーザーがメールアドレスとパスワードを送信し、DBにユーザーを作成する処理である。

## 4.1 API

```http
POST /auth/register
```

リクエスト例：

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

レスポンス例：

```json
{
  "id": 1,
  "email": "user@example.com"
}
```

## 4.2 処理の流れ

```text
Next.js
  ↓ POST /auth/register
routers/auth.py
  ↓ request: UserRegisterRequest で入力チェック
services/auth_service.py
  ↓ メール重複確認
repositories/user_repository.py
  ↓ DBから同じメールのユーザーを検索
core/security.py
  ↓ パスワードをハッシュ化
repositories/user_repository.py
  ↓ usersテーブルに保存
routers/auth.py
  ↓ UserResponseとして返却
Next.js
```

## 4.3 コード例

### routers/auth.py

```python
# app/routers/auth.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    return register_user(db, request)

@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    return login_user(db, request)
```

### services/auth_service.py

```python
# app/services/auth_service.py

from fastapi import HTTPException
from app.schemas.auth import UserRegisterRequest, UserLoginRequest
from app.repositories.user_repository import get_user_by_email, create_user
from app.core.security import hash_password, verify_password, create_access_token

def register_user(db, request: UserRegisterRequest):
    existing_user = get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(request.password)
    user = create_user(db, email=request.email, hashed_password=hashed)
    return user

def login_user(db, request: UserLoginRequest):
    user = get_user_by_email(db, request.email)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}
```

### repositories/user_repository.py

```python
# app/repositories/user_repository.py

from sqlalchemy.orm import Session
from app.models.user import User

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str, hashed_password: str):
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

---

# 5. 処理フロー2：ログインと認証

ログインでは、ユーザーのメールアドレスとパスワードを確認し、正しければJWTアクセストークンを返す。

## 5.1 API

```http
POST /auth/login
```

リクエスト例：

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

レスポンス例：

```json
{
  "access_token": "xxxxx.yyyyy.zzzzz",
  "token_type": "bearer"
}
```

## 5.2 ログイン処理の流れ

```text
Next.js
  ↓ POST /auth/login
routers/auth.py
  ↓ UserLoginRequestで入力チェック
services/auth_service.py
  ↓
repositories/user_repository.py
  ↓ emailでユーザー検索
core/security.py
  ↓ verify_password() でパスワード確認
core/security.py
  ↓ create_access_token() でJWT作成
routers/auth.py
  ↓ tokenを返却
Next.js
  ↓ tokenを保存
以降のAPIリクエストでAuthorizationヘッダに付ける
```

## 5.3 認証が必要なAPIの流れ

例えばプロフィール取得APIでは、ログイン中のユーザーだけがアクセスできるようにする。

```http
GET /me/profile
Authorization: Bearer <access_token>
```

処理の流れは以下である。

```text
Next.js
  ↓ GET /me/profile + Authorizationヘッダ
routers/profiles.py
  ↓ Depends(get_current_user)
core/security.py
  ↓ JWTを検証
core/security.py
  ↓ token内のuser_idを取得
repositories/user_repository.py
  ↓ user_idからユーザーを取得
routers/profiles.py
  ↓ current_userとして利用
services/profile_service.py
  ↓ プロフィール取得
Next.js
```

つまり、ログイン後のAPIでは、毎回アクセストークンから現在のユーザーを確認する。

---

# 6. 処理フロー3：プロフィール登録・更新

プロフィールは、マッチングに使うユーザー属性である。

## 6.1 API

```http
PUT /me/profile
```

リクエスト例：

```json
{
  "prefecture": "京都府",
  "city": "京都市",
  "ward": "左京区",
  "birth_date": "2003-04-01",
  "gender": "male",
  "is_single": true,
  "has_spouse": false,
  "has_children": false,
  "annual_income": 1200000,
  "is_tax_exempt_household": false,
  "employment_status": "student",
  "is_student": true,
  "is_single_parent": false,
  "is_disabled": false
}
```

## 6.2 処理の流れ

```text
Next.js
  ↓ PUT /me/profile
routers/profiles.py
  ↓ Authorizationヘッダからログインユーザー確認
schemas/profile.py
  ↓ ProfileRequestで入力チェック
services/profile_service.py
  ↓ 既存プロフィールがあるか確認
repositories/profile_repository.py
  ↓ あれば更新、なければ作成
DB
  ↓
ProfileResponseとして返却
```

## 6.3 コード例

### routers/profiles.py

```python
# app/routers/profiles.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.profile import ProfileRequest, ProfileResponse
from app.services.profile_service import get_my_profile, upsert_my_profile

router = APIRouter(prefix="/me", tags=["profiles"])

@router.get("/profile", response_model=ProfileResponse)
def read_my_profile(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return get_my_profile(db, current_user.id)

@router.put("/profile", response_model=ProfileResponse)
def update_my_profile(
    request: ProfileRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return upsert_my_profile(db, current_user.id, request)
```

### services/profile_service.py

```python
# app/services/profile_service.py

from fastapi import HTTPException
from app.repositories.profile_repository import get_profile_by_user_id, create_profile, update_profile

def get_my_profile(db, user_id: int):
    profile = get_profile_by_user_id(db, user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

def upsert_my_profile(db, user_id: int, request):
    profile = get_profile_by_user_id(db, user_id)

    if profile is None:
        return create_profile(db, user_id, request)

    return update_profile(db, profile, request)
```

### repositories/profile_repository.py

```python
# app/repositories/profile_repository.py

from sqlalchemy.orm import Session
from app.models.profile import UserProfile

def get_profile_by_user_id(db: Session, user_id: int):
    return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

def create_profile(db: Session, user_id: int, request):
    profile = UserProfile(user_id=user_id, **request.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_profile(db: Session, profile: UserProfile, request):
    for key, value in request.model_dump().items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile
```

---

# 7. 処理フロー4：支援制度一覧・詳細取得

制度情報は、マッチングの材料になる。

## 7.1 API

制度一覧：

```http
GET /programs
```

制度詳細：

```http
GET /programs/{program_id}
```

## 7.2 処理の流れ

```text
Next.js
  ↓ GET /programs
routers/programs.py
  ↓ クエリパラメータを受け取る
services/program_service.py
  ↓
repositories/program_repository.py
  ↓ support_programsテーブルから取得
DB
  ↓
制度一覧として返却
```

## 7.3 コード例

### routers/programs.py

```python
# app/routers/programs.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.program_service import list_programs, get_program_detail

router = APIRouter(prefix="/programs", tags=["programs"])

@router.get("")
def read_programs(
    category: str | None = None,
    city: str | None = None,
    db: Session = Depends(get_db),
):
    return list_programs(db, category=category, city=city)

@router.get("/{program_id}")
def read_program(program_id: int, db: Session = Depends(get_db)):
    return get_program_detail(db, program_id)
```

### repositories/program_repository.py

```python
# app/repositories/program_repository.py

from sqlalchemy.orm import Session, joinedload
from app.models.support_program import SupportProgram

def get_active_programs(db: Session):
    return db.query(SupportProgram).filter(SupportProgram.is_active == True).all()

def get_active_programs_with_conditions(db: Session):
    return (
        db.query(SupportProgram)
        .options(joinedload(SupportProgram.condition))
        .filter(SupportProgram.is_active == True)
        .all()
    )

def get_program_by_id(db: Session, program_id: int):
    return db.query(SupportProgram).filter(SupportProgram.id == program_id).first()

def search_programs(db: Session, category: str | None = None, city: str | None = None):
    query = db.query(SupportProgram).filter(SupportProgram.is_active == True)

    if category:
        query = query.filter(SupportProgram.category == category)

    if city:
        query = query.filter(SupportProgram.target_city == city)

    return query.all()
```

---

# 8. 処理フロー5：マッチング処理

このアプリの中核である。

前提として、プロトタイプでは **マッチング結果を事前に保存しない**。

基本方針は以下である。

```text
ユーザーがマッチ結果画面を開く
  ↓
Next.js が GET /me/matches を呼ぶ
  ↓
FastAPI がその場でマッチングを実行する
  ↓
結果を返す
```

つまり、マッチング処理の実行タイミングは、

```text
GET /me/matches が呼ばれた瞬間
```

である。

---

## 8.1 API

```http
GET /me/matches
```

ヘッダ：

```http
Authorization: Bearer <access_token>
```

レスポンス例：

```json
[
  {
    "program_id": 1,
    "title": "住居確保給付金",
    "provider": "京都市",
    "summary": "離職等により住居を失うおそれのある方に家賃相当額を支給します。",
    "benefit": "家賃相当額を一定期間支給",
    "category": "housing",
    "score": 85,
    "status": "eligible",
    "reasons": [
      "居住地が対象地域に含まれています",
      "年収条件を満たしている可能性があります"
    ],
    "warnings": [
      "資産額など追加確認が必要な条件があります"
    ],
    "deadline": null,
    "application_url": "https://example.com"
  }
]
```

---

## 8.2 処理の流れ

```text
Next.js
  ↓ GET /me/matches
routers/matches.py
  ↓ Authorizationヘッダからログインユーザー確認
core/security.py
  ↓ get_current_user()
services/matching_service.py
  ↓ ユーザープロフィール取得
repositories/profile_repository.py
  ↓ user_profilesテーブルから取得
services/matching_service.py
  ↓ 有効な制度一覧と条件を取得
repositories/program_repository.py
  ↓ support_programs + support_program_conditionsを取得
services/matching_service.py
  ↓ 各制度に対して calculate_match_score() を実行
services/matching_service.py
  ↓ スコア順に並び替え
routers/matches.py
  ↓ レスポンス返却
Next.js
  ↓ マッチ結果一覧画面に表示
```

---

## 8.3 コード例

### routers/matches.py

```python
# app/routers/matches.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.match import MatchResultResponse
from app.services.matching_service import get_matches_for_user

router = APIRouter(prefix="/me", tags=["matches"])

@router.get("/matches", response_model=List[MatchResultResponse])
def read_my_matches(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return get_matches_for_user(db, current_user.id)
```

### services/matching_service.py

```python
# app/services/matching_service.py

from datetime import date
from fastapi import HTTPException
from app.repositories.profile_repository import get_profile_by_user_id
from app.repositories.program_repository import get_active_programs_with_conditions

def calculate_age(birth_date: date) -> int:
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def get_matches_for_user(db, user_id: int):
    profile = get_profile_by_user_id(db, user_id)
    if profile is None:
        raise HTTPException(status_code=400, detail="Profile is required before matching")

    programs = get_active_programs_with_conditions(db)
    results = []

    for program in programs:
        if program.condition is None:
            continue

        match_result = calculate_match_score(profile, program, program.condition)

        if match_result is not None:
            results.append(match_result)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def calculate_match_score(profile, program, condition):
    score = 0
    reasons = []
    warnings = []
    failed_required_conditions = []

    # 地域条件
    if program.target_prefecture and program.target_prefecture != profile.prefecture:
        failed_required_conditions.append("対象都道府県が一致しません")
    else:
        score += 20
        reasons.append("居住地が対象地域に含まれています")

    if program.target_city and program.target_city != profile.city:
        failed_required_conditions.append("対象市区町村が一致しません")
    else:
        score += 10

    if program.target_ward and program.target_ward != profile.ward:
        failed_required_conditions.append("対象区が一致しません")
    else:
        score += 5

    # 年齢条件
    age = calculate_age(profile.birth_date) if profile.birth_date else None
    if condition.min_age is not None and age is not None and age < condition.min_age:
        failed_required_conditions.append("年齢条件を満たしていません")
    elif condition.max_age is not None and age is not None and age > condition.max_age:
        failed_required_conditions.append("年齢条件を満たしていません")
    elif condition.min_age is not None or condition.max_age is not None:
        if age is None:
            warnings.append("年齢条件の確認が必要です")
        else:
            score += 15
            reasons.append("年齢条件を満たしている可能性があります")

    # 所得条件
    if condition.max_annual_income is not None:
        if profile.annual_income is None:
            warnings.append("所得条件の確認が必要です")
        elif profile.annual_income <= condition.max_annual_income:
            score += 20
            reasons.append("年収条件を満たしている可能性があります")
        else:
            failed_required_conditions.append("年収条件を超えています")

    # 非課税世帯条件
    if condition.requires_tax_exempt is True:
        if profile.is_tax_exempt_household is True:
            score += 15
            reasons.append("非課税世帯の条件を満たしています")
        elif profile.is_tax_exempt_household is None:
            warnings.append("非課税世帯かどうかの確認が必要です")
        else:
            failed_required_conditions.append("非課税世帯向けの制度です")

    # 子ども条件
    if condition.requires_children is True:
        if profile.has_children is True:
            score += 10
            reasons.append("子どもに関する条件を満たしています")
        elif profile.has_children is None:
            warnings.append("子どもの有無について確認が必要です")
        else:
            failed_required_conditions.append("子どもがいる世帯向けの制度です")

    # 学生条件
    if condition.requires_student is True:
        if profile.is_student is True:
            score += 10
            reasons.append("学生向け条件を満たしています")
        elif profile.is_student is None:
            warnings.append("学生かどうかの確認が必要です")
        else:
            failed_required_conditions.append("学生向けの制度です")

    # 失業条件
    if condition.requires_unemployed is True:
        if profile.employment_status == "unemployed":
            score += 15
            reasons.append("雇用状況に関する条件を満たしている可能性があります")
        elif profile.employment_status is None:
            warnings.append("雇用状況の確認が必要です")
        else:
            failed_required_conditions.append("失業中の方向けの制度です")

    if failed_required_conditions:
        return None

    status = "possible" if warnings else "eligible"

    return {
        "program_id": program.id,
        "title": program.title,
        "provider": program.provider,
        "summary": program.summary,
        "benefit": program.benefit,
        "category": program.category,
        "score": score,
        "status": status,
        "reasons": reasons,
        "warnings": warnings,
        "deadline": program.deadline,
        "application_url": program.application_url,
    }
```

---

# 9. マッチングを事前実行する場合との違い

プロトタイプでは、基本的にリアルタイム実行でよい。

しかし、将来的には事前実行型にすることもできる。

## 9.1 現在おすすめする方式：リアルタイム実行

```text
GET /me/matches が呼ばれる
  ↓
その場でマッチング計算
  ↓
結果を返す
```

メリット：

```text
- 実装が簡単
- プロフィール変更後すぐ結果が変わる
- match_resultsテーブルが不要
- 制度件数が少ないプロトタイプでは十分速い
```

デメリット：

```text
- 制度数やユーザー数が増えると遅くなる可能性がある
- 過去のマッチ結果履歴は残らない
```

## 9.2 事前実行型

```text
PUT /me/profile
  ↓
プロフィール保存
  ↓
マッチング再計算
  ↓
match_resultsテーブルに保存

GET /me/matches
  ↓
保存済みのmatch_resultsを取得
```

メリット：

```text
- 表示が速い
- 履歴を残せる
- 大規模化しやすい
```

デメリット：

```text
- 実装が複雑
- 制度情報更新時に再計算が必要
- 古い結果が残る可能性がある
```

プロトタイプでは、まずリアルタイム実行にする。

---

# 10. APIを実際に叩くコマンド例

以下では、ローカルでFastAPIを起動している前提で説明する。

```text
http://localhost:8000
```

## 10.1 サーバー起動

```bash
uvicorn app.main:app --reload
```

起動後、以下にアクセスするとSwagger UIが見られる。

```text
http://localhost:8000/docs
```

---

## 10.2 ヘルスチェック

```bash
curl http://localhost:8000/health
```

レスポンス例：

```json
{
  "status": "ok"
}
```

---

## 10.3 ユーザー登録

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

---

## 10.4 ログイン

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

レスポンス例：

```json
{
  "access_token": "xxxxx.yyyyy.zzzzz",
  "token_type": "bearer"
}
```

この `access_token` を以降のAPIで使う。

---

## 10.5 プロフィール登録・更新

```bash
curl -X PUT http://localhost:8000/me/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "prefecture": "京都府",
    "city": "京都市",
    "ward": "左京区",
    "birth_date": "2003-04-01",
    "gender": "male",
    "is_single": true,
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

---

## 10.6 自分のプロフィール取得

```bash
curl -X GET http://localhost:8000/me/profile \
  -H "Authorization: Bearer <access_token>"
```

---

## 10.7 制度一覧取得

```bash
curl http://localhost:8000/programs
```

カテゴリで絞る場合：

```bash
curl "http://localhost:8000/programs?category=housing"
```

市区町村で絞る場合：

```bash
curl "http://localhost:8000/programs?city=京都市"
```

---

## 10.8 制度詳細取得

```bash
curl http://localhost:8000/programs/1
```

---

## 10.9 マッチング結果取得

```bash
curl -X GET http://localhost:8000/me/matches \
  -H "Authorization: Bearer <access_token>"
```

このリクエストが送られた瞬間に、バックエンド側でマッチング処理が実行される。

---

# 11. Next.jsから呼ぶときのイメージ

ログイン後に取得した `access_token` を使ってAPIを呼ぶ。

例：マッチング結果取得

```typescript
const token = localStorage.getItem("access_token");

const res = await fetch("http://localhost:8000/me/matches", {
  method: "GET",
  headers: {
    "Authorization": `Bearer ${token}`,
  },
});

const matches = await res.json();
console.log(matches);
```

プロフィール更新の例：

```typescript
const token = localStorage.getItem("access_token");

await fetch("http://localhost:8000/me/profile", {
  method: "PUT",
  headers: {
    "Content-Type": "application/json",
    "Authorization": `Bearer ${token}`,
  },
  body: JSON.stringify({
    prefecture: "京都府",
    city: "京都市",
    ward: "左京区",
    birth_date: "2003-04-01",
    gender: "male",
    is_single: true,
    has_spouse: false,
    has_children: false,
    annual_income: 1200000,
    is_tax_exempt_household: false,
    employment_status: "student",
    is_student: true,
    is_single_parent: false,
    is_disabled: false,
  }),
});
```

---

# 12. 実装時に迷いやすいポイント

## 12.1 schemas と models の違い

```text
models/ はDBの形
schemas/ はAPIの入出力の形
```

例：

DBの `users` テーブルには `hashed_password` がある。

しかし、APIレスポンスでは `hashed_password` を返さない。

このように、DBにある情報とAPIで見せる情報は一致しないことがある。

ため、`models/` と `schemas/` を分ける。

---

## 12.2 routers に処理を書きすぎない

悪い例：

```python
@router.get("/matches")
def get_matches():
    # DB取得
    # 条件判定
    # スコア計算
    # ソート
    # レスポンス整形
    ...
```

これだと `routers/` が肥大化する。

良い例：

```python
@router.get("/matches")
def get_matches(...):
    return get_matches_for_user(db, current_user.id)
```

実際の処理は `services/matching_service.py` に置く。

---

## 12.3 services と repositories の違い

```text
services/ は「何をするか」
repositories/ は「DBからどう取るか」
```

例：

```text
matching_service.py
- ユーザーに合う制度を探す
- 条件を判定する
- スコアを計算する

program_repository.py
- 有効な制度一覧をDBから取る
- 制度IDで詳細を取る
```

---

## 12.4 core は便利関数置き場ではない

`core/` は何でも置く場所ではない。

置くべきもの：

```text
- DB接続
- 環境変数
- 認証
- パスワードハッシュ化
- JWT
```

置くべきでないもの：

```text
- マッチング処理
- プロフィール更新処理
- 制度一覧取得処理
```

これらは `services/` に置く。

---

# 13. 最小実装での開発順序

まずは以下の順で作るとよい。

```text
1. app/main.py を作る
2. /health APIを作る
3. core/database.py を作る
4. usersモデルを作る
5. user_repository.py を作る
6. schemas/auth.py を作る
7. auth_service.py を作る
8. routers/auth.py を作る
9. ユーザー登録・ログインをcurlで確認する
10. profileモデル・schema・repository・service・routerを作る
11. プロフィール登録をcurlで確認する
12. support_programモデルを作る
13. seedデータを入れる
14. programs APIを作る
15. matching_service.py を作る
16. /me/matches をcurlで確認する
17. Next.jsと接続する
```

この順番で進めると、常に動作確認しながら開発できる。

---

# 14. バックエンド全体の処理対応表

| 機能       | API                   | router        | service               | repository                                       | model                              |
| -------- | --------------------- | ------------- | --------------------- | ------------------------------------------------ | ---------------------------------- |
| ユーザー登録   | `POST /auth/register` | `auth.py`     | `auth_service.py`     | `user_repository.py`                             | `user.py`                          |
| ログイン     | `POST /auth/login`    | `auth.py`     | `auth_service.py`     | `user_repository.py`                             | `user.py`                          |
| プロフィール取得 | `GET /me/profile`     | `profiles.py` | `profile_service.py`  | `profile_repository.py`                          | `profile.py`                       |
| プロフィール更新 | `PUT /me/profile`     | `profiles.py` | `profile_service.py`  | `profile_repository.py`                          | `profile.py`                       |
| 制度一覧     | `GET /programs`       | `programs.py" | `program_service.py`  | `program_repository.py`                          | `support_program.py`               |
| 制度詳細     | `GET /programs/{id}`  | `programs.py` | `program_service.py`  | `program_repository.py`                          | `support_program.py`               |
| マッチング    | `GET /me/matches`     | `matches.py`  | `matching_service.py` | `profile_repository.py`, `program_repository.py` | `profile.py`, `support_program.py` |

---

# 15. 最終的な理解のための一文まとめ

このバックエンドは、以下のように理解するとよい。

```text
routers/ はAPIの入口。
schemas/ はAPIで受け取る・返すデータの形。
services/ はアプリの処理本体。
repositories/ はDB操作。
models/ はDBテーブル定義。
core/ はDB接続や認証などの共通基盤。
```

そして、マッチング処理は以下のタイミングで実行される。

```text
ユーザーがマッチ結果画面を開く
  ↓
Next.js が GET /me/matches を呼ぶ
  ↓
FastAPIがその場でマッチングを実行する
  ↓
結果を返す
```

プロトタイプでは、このリアルタイム実行方式が最もシンプルで実装しやすい。
