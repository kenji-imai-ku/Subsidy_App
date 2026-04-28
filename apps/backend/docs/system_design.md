# 支援制度マッチングWebアプリ：バックエンド設計書

このドキュメントは、自治体・国の補助金・給付金・支援制度を、ユーザーの状況に応じて推薦するWebアプリのバックエンド設計をまとめたものである。

バックエンドの中心は、次の一文に集約できる。

**ユーザー情報と、構造化された支援制度条件を照合して、「対象になりそうな制度」と「その理由」を返すAPIを作る。**

検索エンジンやAIチャットではなく、まずは **ルールベースのマッチングAPI** として設計する。

---

# 1. 全体アーキテクチャ

想定構成は以下の通りである。

```text
Frontend: Next.js
  ↓ HTTP / JSON
Backend: FastAPI
  ↓ ORM
Database: PostgreSQL
```

バックエンドの責務は大きく5つである。

```text
1. ユーザー登録・ログイン
2. ユーザープロフィール管理
3. 支援制度データ管理
4. マッチング処理
5. マッチ結果の返却
```

初期プロトタイプでは、制度データの自動収集は後回しでよい。

まずは管理者または開発者が、京都市・左京区などの制度を手入力またはCSVで登録する形で十分である。

---

# 2. 最初に作るべき機能スコープ

いきなり全国対応やAI判定を作ると破綻しやすいので、最初はこの範囲に絞るのがよい。

## MVPで作る機能

```text
ユーザー系
- ユーザー登録
- ログイン
- 自分のプロフィール登録・更新
- 自分のプロフィール取得

制度系
- 支援制度一覧取得
- 支援制度詳細取得
- 開発者用の制度登録API

マッチング系
- 自分に合う制度一覧取得
- 各制度について「なぜ対象になりそうか」を返す
- マッチ度スコアを返す
```

## 後回しでよい機能

```text
- LINE通知
- AIチャット
- 制度の自動スクレイピング
- 全国自治体対応
- 申請書類の自動作成
- 管理画面の本格実装
```

---

# 3. バックエンドのフォルダ構成

FastAPIでは、最初はこの構成が分かりやすい。

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── support_program.py
│   │   └── match_result.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── support_program.py
│   │   └── match.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── users.py
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

それぞれの役割は以下の通りである。

```text
routers/
APIの入口。URLごとの処理を書く。

schemas/
リクエスト・レスポンスの型を書く。Pydantic。

models/
DBのテーブル定義を書く。SQLAlchemy。

services/
ビジネスロジックを書く。マッチング処理はここ。

repositories/
DBアクセス処理を書く。

core/
DB接続、設定、認証処理など共通部分。
```

小規模なら `repositories` は省略してもよいが、2人で開発するなら分けた方が衝突しにくい。

---

# 4. データベース設計

このアプリで一番重要なのはDB設計である。

特に、制度情報をただの文章として持つのではなく、**制度本体** と **条件** を分けて持つことが重要である。

## テーブル全体像

```text
users
- ユーザーアカウント

user_profiles
- ユーザーの属性・生活状況

support_programs
- 支援制度本体

support_program_conditions
- 支援制度の条件

match_histories
- マッチング実行履歴、必要なら後で追加
```

最初は `match_histories` はなくてもよい。

---

# 5. users テーブル

ユーザー登録・ログイン用である。

```sql
users
```

| カラム             | 型              | 説明         |
| --------------- | -------------- | ---------- |
| id              | UUID / Integer | ユーザーID     |
| email           | varchar        | メールアドレス    |
| hashed_password | varchar        | ハッシュ化パスワード |
| created_at      | timestamp      | 作成日時       |
| updated_at      | timestamp      | 更新日時       |

ポイントは、**パスワードをそのまま保存しない**ことである。

```text
password → bcryptなどでハッシュ化 → hashed_passwordとして保存
```

---

# 6. user_profiles テーブル

マッチングに使うユーザー情報である。

```sql
user_profiles
```

| カラム                     | 型              | 例          | 説明          |
| ----------------------- | -------------- | ---------- | ----------- |
| id                      | UUID / Integer | 1          | プロフィールID    |
| user_id                 | UUID / Integer | 1          | usersへの外部キー |
| prefecture              | varchar        | 京都府        | 都道府県        |
| city                    | varchar        | 京都市        | 市区町村        |
| ward                    | varchar        | 左京区        | 区           |
| birth_date              | date           | 2003-04-01 | 生年月日        |
| gender                  | varchar        | male       | 性別          |
| is_single               | boolean        | true       | 独身か         |
| has_spouse              | boolean        | false      | 配偶者の有無      |
| has_children            | boolean        | false      | 子どもの有無      |
| annual_income           | integer        | 1200000    | 年収          |
| is_tax_exempt_household | boolean        | false      | 非課税世帯か      |
| employment_status       | varchar        | student    | 雇用状況        |
| is_student              | boolean        | true       | 学生か         |
| is_single_parent        | boolean        | false      | ひとり親か       |
| is_disabled             | boolean        | false      | 障害の有無       |
| created_at              | timestamp      |            | 作成日時        |
| updated_at              | timestamp      |            | 更新日時        |

雇用状況は文字列で持ってもよいが、値は固定した方がよい。

```text
employed
part_time
unemployed
student
self_employed
retired
other
```

初期段階では、細かすぎる属性は不要である。

まずは以下だけでも成立する。

```text
居住地
生年月日
性別
世帯構成（独身・配偶者・子供）
年収
非課税世帯かどうか
雇用状況
学生かどうか
```

---

# 7. support_programs テーブル

制度そのものの情報である。

```sql
support_programs
```

| カラム                | 型              | 例           | 説明     |
| ------------------ | -------------- | ----------- | ------ |
| id                 | UUID / Integer | 1           | 制度ID   |
| title              | varchar        | 住居確保給付金     | 制度名    |
| provider           | varchar        | 京都市         | 実施主体   |
| summary            | text           | 家賃相当額を支給... | 概要     |
| benefit            | text           | 月額上限〇万円     | 支援内容   |
| category           | varchar        | housing     | カテゴリ   |
| target_prefecture  | varchar        | 京都府         | 対象都道府県 |
| target_city        | varchar        | 京都市         | 対象市区町村 |
| target_ward        | varchar        | 左京区 / null  | 対象区    |
| application_url    | text           | URL         | 申請先    |
| deadline           | date / null    | 2026-06-30  | 締切     |
| required_documents | text           | 本人確認書類など    | 必要書類   |
| source_url         | text           | URL         | 情報源    |
| is_active          | boolean        | true        | 掲載中か   |
| created_at         | timestamp      |             | 作成日時   |
| updated_at         | timestamp      |             | 更新日時   |

カテゴリは最初は固定でよい。

```text
housing
childcare
education
employment
living
medical
disability
other
```

---

# 8. support_program_conditions テーブル

ここが最重要である。

制度条件を文章ではなく、機械的に判定しやすい形で保存する。

ただし、最初から複雑な条件式エンジンを作る必要はない。

プロトタイプでは、制度1件につき条件1レコードにするのが簡単である。

```sql
support_program_conditions
```

| カラム                    | 型              | 例       | 説明            |
| ---------------------- | -------------- | ------- | ------------- |
| id                     | UUID / Integer | 1       | 条件ID          |
| program_id             | UUID / Integer | 1       | 制度ID          |
| min_age                | integer / null | 18      | 最低年齢          |
| max_age                | integer / null | 65      | 最高年齢          |
| max_annual_income      | integer / null | 2000000 | 年収上限          |
| requires_tax_exempt    | boolean / null | true    | 非課税世帯である必要があるか |
| min_household_size     | integer / null | 1       | 最低世帯人数        |
| requires_children      | boolean / null | true    | 子どもが必要か       |
| requires_student       | boolean / null | true    | 学生である必要があるか   |
| requires_unemployed    | boolean / null | true    | 失業中である必要があるか  |
| requires_single_parent | boolean / null | true    | ひとり親である必要があるか |
| requires_disabled      | boolean / null | true    | 障害がある必要があるか   |
| condition_description  | text           | 対象条件の文章 | 人間向け説明        |

`null` の意味は **条件なし** である。

例えば、

```text
max_annual_income = null
```

なら、所得条件は判定しない。

```text
requires_tax_exempt = true
```

なら、非課税世帯である必要がある。

---

# 9. 条件設計の考え方

制度条件は、まず以下の3種類に分けるとよい。

## 1. 必須条件

満たさないと対象外になる条件。

例：

```text
京都市在住である
年収が一定以下である
非課税世帯である
失業中である
子どもがいる
学生である
```

## 2. 加点条件

満たすと優先度が上がる条件。

例：

```text
世帯人数が多い
ひとり親である
収入がかなり低い
締切が近い
```

## 3. 不明条件

ユーザー情報だけでは判定できない条件。

例：

```text
資産額
預貯金額
家賃額
在留資格
過去の受給歴
```

このアプリでは、不明条件がある制度を完全に除外するのではなく、

```text
対象の可能性あり。ただし追加確認が必要。
```

として表示するのがよい。

---

# 10. マッチングロジック設計

最初のマッチングは、次の流れで十分である。

```text
1. ログインユーザーのプロフィールを取得
2. 有効な支援制度一覧を取得
3. 各制度の条件を取得
4. 必須条件をチェック
5. 加点条件をチェック
6. スコアを計算
7. スコア順に並べて返す
```

## マッチング結果の分類

結果は3段階にすると分かりやすい。

```text
eligible
対象になりそう

possible
対象の可能性あり・追加確認が必要

not_eligible
対象外の可能性が高い
```

ただし、フロントに返すのは `eligible` と `possible` だけでよい。

---

# 11. スコア計算の例

例えば100点満点で考える。

```text
地域一致: 30点
年齢条件一致: 15点
所得条件一致: 20点
雇用条件一致: 15点
子ども条件一致: 10点
その他条件一致: 10点
```

必須条件に落ちた場合は、基本的に除外する。

ただし、情報不足の場合は除外せず、`possible` にする。

## 疑似コード

```python
def calculate_match_score(profile, program, condition):
    score = 0
    reasons = []
    warnings = []
    failed_required_conditions = []

    # 地域条件
    if program.target_prefecture and program.target_prefecture != profile.prefecture:
        failed_required_conditions.append("対象地域が一致しません")
    else:
        score += 30
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
    if condition.min_age is not None and profile.age < condition.min_age:
        failed_required_conditions.append("年齢条件を満たしていません")
    elif condition.max_age is not None and profile.age > condition.max_age:
        failed_required_conditions.append("年齢条件を満たしていません")
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

    # 子ども条件
    if condition.requires_children is True:
        if profile.has_children:
            score += 10
            reasons.append("子どもに関する条件を満たしています")
        else:
            failed_required_conditions.append("子どもがいる世帯向けの制度です")

    # 学生条件
    if condition.requires_student is True:
        if profile.is_student:
            score += 10
            reasons.append("学生向け条件を満たしています")
        else:
            failed_required_conditions.append("学生向けの制度です")

    # 失業条件
    if condition.requires_unemployed is True:
        if profile.employment_status == "unemployed":
            score += 15
            reasons.append("雇用状況に関する条件を満たしている可能性があります")
        else:
            failed_required_conditions.append("失業中の方向けの制度です")

    if failed_required_conditions:
        return None

    if warnings:
        status = "possible"
    else:
        status = "eligible"

    return {
        "program_id": program.id,
        "score": score,
        "status": status,
        "reasons": reasons,
        "warnings": warnings,
    }
```

このように、単に制度を返すのではなく、

```text
なぜ対象になりそうなのか
どこに追加確認が必要なのか
```

を返すのが重要である。

---

# 12. API設計

フロントエンドとつなぐために、APIは最初から整理しておくべきである。

---

## 認証系API

### ユーザー登録

```http
POST /auth/register
```

リクエスト：

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

レスポンス：

```json
{
  "id": 1,
  "email": "user@example.com"
}
```

---

### ログイン

```http
POST /auth/login
```

リクエスト：

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

レスポンス：

```json
{
  "access_token": "xxxxx.yyyyy.zzzzz",
  "token_type": "bearer"
}
```

JWT認証を使う想定である。

---

## プロフィールAPI

### 自分のプロフィール取得

```http
GET /me/profile
```

レスポンス：

```json
{
  "prefecture": "京都府",
  "city": "京都市",
  "ward": "左京区",
  "age": 23,
  "household_size": 1,
  "annual_income": 1200000,
  "employment_status": "student",
  "has_children": false,
  "is_student": true,
  "is_single_parent": false,
  "is_disabled": false
}
```

---

### プロフィール作成・更新

```http
PUT /me/profile
```

リクエスト：

```json
{
  "prefecture": "京都府",
  "city": "京都市",
  "ward": "左京区",
  "age": 23,
  "household_size": 1,
  "annual_income": 1200000,
  "employment_status": "student",
  "has_children": false,
  "is_student": true,
  "is_single_parent": false,
  "is_disabled": false
}
```

レスポンス：

```json
{
  "message": "profile updated"
}
```

---

## 制度API

### 支援制度一覧取得

```http
GET /programs
```

クエリ例：

```http
GET /programs?category=housing&city=京都市
```

レスポンス：

```json
[
  {
    "id": 1,
    "title": "住居確保給付金",
    "provider": "京都市",
    "summary": "離職等により住居を失うおそれのある方に家賃相当額を支給します。",
    "benefit": "家賃相当額を一定期間支給",
    "category": "housing",
    "target_prefecture": "京都府",
    "target_city": "京都市",
    "target_ward": null,
    "deadline": null
  }
]
```

---

### 支援制度詳細取得

```http
GET /programs/{program_id}
```

レスポンス：

```json
{
  "id": 1,
  "title": "住居確保給付金",
  "provider": "京都市",
  "summary": "離職等により住居を失うおそれのある方に家賃相当額を支給します。",
  "benefit": "家賃相当額を一定期間支給",
  "category": "housing",
  "target_prefecture": "京都府",
  "target_city": "京都市",
  "target_ward": null,
  "application_url": "https://example.com",
  "required_documents": "本人確認書類、収入確認書類など",
  "condition_description": "離職等により経済的に困窮し、住居を失うおそれがある方。"
}
```

---

## マッチングAPI

### 自分に合う制度を取得

```http
GET /me/matches
```

レスポンス：

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
      "年収条件を満たしている可能性があります",
      "雇用状況に関する条件を満たしている可能性があります"
    ],
    "warnings": [
      "資産額など追加確認が必要な条件があります"
    ],
    "deadline": null,
    "application_url": "https://example.com"
  }
]
```

ここで大事なのは、フロントがそのまま画面表示に使える形で返すことである。

---

# 13. 画面とAPIの対応関係

フロントと話すときは、画面単位でAPIを整理すると分かりやすい。

| 画面         | 必要なAPI                               |
| ---------- | ------------------------------------ |
| 新規登録画面     | `POST /auth/register`                |
| ログイン画面     | `POST /auth/login`                   |
| プロフィール入力画面 | `GET /me/profile`, `PUT /me/profile` |
| マッチ結果一覧画面  | `GET /me/matches`                    |
| 制度詳細画面     | `GET /programs/{program_id}`         |
| 制度一覧画面     | `GET /programs`                      |

---

# 14. 制度データの登録方法

プロトタイプでは、まずCSVかPythonスクリプトでDBに入れるのがよい。

例えば、`seed_programs.py` を作る。

```text
app/seed/seed_programs.py
```

中身のイメージ：

```python
programs = [
    {
        "title": "住居確保給付金",
        "provider": "京都市",
        "summary": "離職等により住居を失うおそれのある方に家賃相当額を支給します。",
        "benefit": "家賃相当額を一定期間支給",
        "category": "housing",
        "target_prefecture": "京都府",
        "target_city": "京都市",
        "target_ward": None,
        "application_url": "https://example.com",
        "condition": {
            "max_annual_income": 2000000,
            "requires_unemployed": True
        }
    }
]
```

最初は10件程度で十分である。

制度件数よりも、**条件が構造化されていてマッチングできること**の方が大事である。

---

# 15. 開発の進め方

2人でバックエンドを作るなら、最初から完全に分業するより、最初に松岡さんが骨組みを作ってから分けるのがよい。

## Phase 1：バックエンドの土台作成

担当：松岡さん

```text
- FastAPIプロジェクト作成
- PostgreSQL接続
- SQLAlchemy設定
- Alembic設定
- usersテーブル作成
- health check API作成
```

最初に作るAPI：

```http
GET /health
```

レスポンス：

```json
{
  "status": "ok"
}
```

これでバックエンドが起動していることを確認できる。

---

## Phase 2：認証・プロフィール

担当を分けるなら、以下のようにする。

### 松岡さん

```text
- DB設計
- users / profiles のモデル作成
- 認証方式の設計
- API仕様の決定
```

### もう一人

```text
- プロフィールAPI実装
- バリデーション実装
- テストデータ作成
```

この段階で作るAPI：

```text
POST /auth/register
POST /auth/login
GET /me/profile
PUT /me/profile
```

---

## Phase 3：制度データ

### 松岡さん

```text
- support_programs のDB設計
- support_program_conditions のDB設計
- 制度条件の持ち方を決める
```

### もう一人

```text
- 制度一覧API
- 制度詳細API
- seedデータ作成
```

この段階で作るAPI：

```text
GET /programs
GET /programs/{program_id}
```

---

## Phase 4：マッチング

ここはアプリの中核なので、松岡さんが主導した方がよい。

### 松岡さん

```text
- matching_service.py の設計
- スコア計算ロジック実装
- reasons / warnings の設計
```

### もう一人

```text
- マッチングAPIのルーター実装
- レスポンス整形
- テストケース作成
```

この段階で作るAPI：

```text
GET /me/matches
```

---

## Phase 5：フロントとの統合

```text
- CORS設定
- 認証トークンの受け渡し確認
- Next.jsからAPI呼び出し
- レスポンス形式の調整
- エラー時の表示確認
```

---

# 16. 2人の役割分担案

バックエンド2人なら、以下のように分けるのが自然である。

## 松岡さん：設計・中核ロジック担当

```text
- DB設計
- API仕様設計
- マッチングロジック設計
- コードレビュー
- フロントとの接続方針決定
- GitHub Issue作成
- 統合時の調整
```

## もう一人：API実装・データ整備担当

```text
- プロフィールAPI実装
- 制度一覧API実装
- 制度詳細API実装
- seedデータ作成
- テストデータ登録
- API動作確認
```

ただし、認証はミスると詰まりやすいので、松岡さんが設計して、実装は一緒に確認するのがよい。

---

# 17. GitHub Issueの切り方

実際の開発では、以下のようにIssueに分けるとよい。

```text
#1 FastAPIプロジェクトの初期セットアップ
#2 PostgreSQL接続設定
#3 usersテーブルの作成
#4 ユーザー登録APIの実装
#5 ログインAPIの実装
#6 user_profilesテーブルの作成
#7 プロフィール取得APIの実装
#8 プロフィール更新APIの実装
#9 support_programsテーブルの作成
#10 support_program_conditionsテーブルの作成
#11 制度一覧APIの実装
#12 制度詳細APIの実装
#13 seedデータ投入スクリプトの作成
#14 マッチングロジックの実装
#15 マッチ結果APIの実装
#16 CORS設定
#17 Next.jsとの接続確認
#18 READMEに起動手順を書く
```

2人なら、1 Issue = 1 Pull Request くらいがちょうどよい。

---

# 18. 最初の実装順序

実装順序は以下がおすすめである。

```text
1. FastAPI起動
2. PostgreSQL接続
3. usersテーブル作成
4. ユーザー登録
5. ログイン
6. profilesテーブル作成
7. プロフィール保存
8. programsテーブル作成
9. conditionsテーブル作成
10. seedデータ投入
11. 制度一覧取得
12. 制度詳細取得
13. マッチングロジック
14. マッチ結果API
15. フロント統合
```

特に大事なのは、**マッチング機能を最後に作ること**である。

先にユーザー情報と制度データがDBに入っていないと、マッチングのテストができない。

---

# 19. 技術選定について

今回の構成はかなり妥当である。

```text
FastAPI
Pythonでマッチングロジックを書きやすい。
API仕様も自動でSwaggerに出せる。

PostgreSQL
制度データ、ユーザーデータ、条件データを整理して保存しやすい。

SQLAlchemy
PythonからDBを扱いやすい。

Alembic
DB変更履歴を管理できる。

JWT
ログイン状態の管理に使える。
```

プロトタイプなら、この構成で十分である。

逆に、最初から以下を入れる必要は低い。

```text
- Redis
- Elasticsearch
- GraphQL
- Kubernetes
- 複雑なマイクロサービス
- LLM判定
```

---

# 20. 最初のDB設計で注意すること

特に注意すべき点は3つである。

## 1. 制度条件を文章だけで保存しない

これはNGである。

```text
対象者：京都市在住で、失業中で、収入が一定以下の方
```

これだけだと、機械的に判定できない。

必ず以下のように分ける。

```json
{
  "target_city": "京都市",
  "requires_unemployed": true,
  "max_annual_income": 2000000
}
```

---

## 2. 判定不能な条件を無理に判定しない

行政制度には、ユーザー情報だけでは判定できない条件が多い。

例えば、

```text
預貯金額
資産
家賃
離職理由
過去の受給歴
住民税非課税かどうか
```

こういうものは無理に判定せず、

```text
追加確認が必要
```

として返すべきである。

---

## 3. 「対象です」と断定しない

法的・行政的には、アプリ側で断定しない方が安全である。

表示文言は、

```text
対象になる可能性があります
条件を満たす可能性があります
申請前に公式情報を確認してください
```

にするのがよい。

---

# 21. レスポンスで返すべき文言

マッチ結果では、単にスコアだけ返すとユーザーに伝わらない。

必ず理由を返すべきである。

例：

```json
{
  "title": "住居確保給付金",
  "score": 85,
  "status": "eligible",
  "reasons": [
    "京都市在住のため、対象地域に含まれています",
    "入力された年収が制度の所得条件内にあります",
    "現在の雇用状況が制度条件に近いです"
  ],
  "warnings": [
    "預貯金額など、追加確認が必要な条件があります",
    "最終的な対象可否は公式窓口で確認してください"
  ]
}
```

この `reasons` が、アプリの価値になる。

---

# 22. まず目指す完成形

最初の完成形は、これで十分である。

```text
1. ユーザーが登録・ログインできる
2. プロフィールを入力できる
3. DBに10件程度の支援制度が入っている
4. プロフィールに応じて制度が並び替えられる
5. 各制度について「なぜ候補に出たのか」が表示される
6. 公式サイトへのリンクに飛べる
```

これができれば、プロトタイプとしてはかなり形になる。

---

# 23. バックエンドの設計まとめ

最終的な設計方針は以下である。

```text
バックエンドの中核：
支援制度データと制度条件を構造化してDBに保存し、
ユーザープロフィールと照合して、
対象可能性の高い制度を理由付きで返すAPIを作る。

最初に作るもの：
認証、プロフィール、制度一覧、制度詳細、マッチングAPI。

DB設計の中心：
users
user_profiles
support_programs
support_program_conditions

マッチングの中心：
必須条件チェック
加点条件チェック
判定不能条件のwarning化
スコア順ソート
理由付きレスポンス

開発方針：
まず小さく作る。
制度件数は少なくてよい。
AIや通知は後回し。
条件データ設計を最優先する。
```

松岡さんが最初にやるべきことは、コードを書く前にこの3つを決めることである。

```text
1. ユーザープロフィールにどの項目を持たせるか
2. 制度条件をどのカラムで表現するか
3. マッチ結果をどのJSON形式でフロントに返すか
```

ここが決まれば、バックエンド開発はかなり進めやすくなる。
