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
Database: SQLite (初期プロトタイプ用)
```

バックエンドの責務は大きく3つである。

```text
1. ユーザープロフィール管理
2. 支援制度データ管理
3. マッチング処理と結果の返却
```

初期プロトタイプでは、制度データの自動収集は後回しでよい。
まずは管理者または開発者が、京都市・左京区などの制度を手入力またはCSVで登録する形で十分である。
また、開発をシンプルにするため、**ユーザー認証（ログイン機能）は含めない。**

---

# 2. 最初に作るべき機能スコープ

いきなり全国対応やAI判定を作ると破綻しやすいので、最初はこの範囲に絞る。

## MVPで作る機能

```text
プロフィール系
- プロフィールの登録・更新
- プロフィールの取得

制度系
- 支援制度一覧取得
- 支援制度詳細取得
- 開発者用の制度登録API（seedスクリプト等）

マッチング系
- プロフィールに合う制度一覧取得
- 各制度について「なぜ対象になりそうか」を返す
- マッチ度スコアを返す
```

## 後回しでよい機能

```text
- ユーザー認証・ログイン
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
DB接続、設定など共通部分。
```

---

# 4. データベース設計

特に、制度情報をただの文章として持つのではなく、**制度本体** と **条件** を分けて持つことが重要である。

## テーブル全体像

```text
user_profiles
- ユーザーの属性・生活状況（認証なしのため、1レコードのみ、またはセッション単位で管理）

support_programs
- 支援制度本体

support_program_conditions
- 支援制度の条件
```

---

# 5. user_profiles テーブル

マッチングに使うユーザー情報である。
※ `birth_date` からマッチング時に `age`（年齢）を計算して使用する。

```sql
user_profiles
```

| カラム                     | 型              | 例          | 説明          |
| ----------------------- | -------------- | ---------- | ----------- |
| id                      | UUID / Integer | 1          | プロフィールID    |
| user_id                 | UUID / Integer | 1          | 内部管理用ID      |
| prefecture              | varchar        | 京都府        | 都道府県        |
| city                    | varchar        | 京都市        | 市区町村        |
| ward                    | varchar        | 左京区        | 区           |
| birth_date              | date           | 2003-04-01 | 生年月日        |
| gender                  | varchar        | male       | 性別（出産支援等の判定に使用） |
| has_spouse              | boolean        | false      | 配偶者の有無（配偶者控除等の判定に使用） |
| has_children            | boolean        | false      | 子どもの有無      |
| annual_income           | integer        | 1200000    | 年収          |
| is_tax_exempt_household | boolean        | false      | 非課税世帯か      |
| employment_status       | varchar        | student    | 雇用状況        |
| is_student              | boolean        | true       | 学生か         |
| is_single_parent        | boolean        | false      | ひとり親か       |
| is_disabled             | boolean        | false      | 障害の有無       |
| created_at              | timestamp      |            | 作成日時        |
| updated_at              | timestamp      |            | 更新日時        |

雇用状況の値の例：
```text
employed (会社員)
part_time (アルバイト・パート)
unemployed (離職中)
student (学生)
self_employed (自営業)
retired (年金生活)
other (その他)
```

---

# 6. support_programs テーブル

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

---

# 7. support_program_conditions テーブル

制度条件を機械的に判定しやすい形で保存する。

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
| requires_children      | boolean / null | true    | 子どもが必要か       |
| requires_student       | boolean / null | true    | 学生である必要があるか   |
| requires_unemployed    | boolean / null | true    | 失業中である必要があるか  |
| requires_single_parent | boolean / null | true    | ひとり親である必要があるか |
| requires_disabled      | boolean / null | true    | 障害がある必要があるか   |
| condition_description  | text           | 対象条件の文章 | 人間向け説明        |

---

# 8. 条件設計の考え方

## 1. 必須条件
満たさないと対象外になる条件（地域、年齢上限、所得上限、特定の属性要求など）。

## 2. 加点条件
満たすと優先度が上がる条件。

## 3. 不明条件
資産額など、ユーザー情報だけでは判定できない条件。これらは「追加確認が必要」として表示する。

---

# 9. マッチングロジック設計

1. プロフィールを取得（認証なしのため、最新の1件または特定のIDを使用）
2. 制度条件と照合
3. 各項目でスコアを計算
4. `eligible` (合致), `possible` (可能性あり) に分類して返す

---

# 10. スコア計算の例 (合計100点満点)

- **地域一致: 30点** (都道府県15点, 市区町村10点, 区5点)
- **年齢条件一致: 15点**
- **所得・税条件一致: 25点** (年収15点, 非課税10点)
- **世帯・雇用条件一致: 30点** (雇用10点, 子ども10点, ひとり親5点, 障害5点)

## 疑似コード

```python
def calculate_match_score(profile, program, condition):
    # 生年月日から年齢を計算 (簡易版)
    age = calculate_age(profile.birth_date)
    
    score = 0
    reasons = []
    warnings = []
    failed_required_conditions = []

    # 地域条件 (30点)
    if program.target_prefecture and program.target_prefecture != profile.prefecture:
        failed_required_conditions.append("対象地域（都道府県）が一致しません")
    else:
        score += 15
        reasons.append("居住地が対象都道府県に含まれています")
        if program.target_city:
            if program.target_city != profile.city:
                failed_required_conditions.append("対象地域（市区町村）が一致しません")
            else:
                score += 10
                if program.target_ward:
                    if program.target_ward != profile.ward:
                        failed_required_conditions.append("対象地域（区）が一致しません")
                    else:
                        score += 5

    # 年齢条件 (15点)
    if condition.min_age is not None and age < condition.min_age:
        failed_required_conditions.append("最低年齢条件を満たしていません")
    elif condition.max_age is not None and age > condition.max_age:
        failed_required_conditions.append("最高年齢条件を満たしていません")
    else:
        score += 15
        reasons.append("年齢条件を満たしています")

    # 所得条件 (15点)
    if condition.max_annual_income is not None:
        if profile.annual_income is None:
            warnings.append("所得条件の確認が必要です")
        elif profile.annual_income <= condition.max_annual_income:
            score += 15
            reasons.append("年収が所得制限内です")
        else:
            failed_required_conditions.append("所得制限を超えています")

    # 非課税世帯条件 (10点)
    if condition.requires_tax_exempt is True:
        if profile.is_tax_exempt_household:
            score += 10
            reasons.append("住民税非課税世帯の条件を満たしています")
        else:
            failed_required_conditions.append("住民税非課税世帯向けの制度です")

    # 雇用・学生条件 (10点)
    if condition.requires_unemployed is True:
        if profile.employment_status == "unemployed":
            score += 10
            reasons.append("離職中の方針条件を満たしています")
        else:
            failed_required_conditions.append("離職中の方向けの制度です")
    elif condition.requires_student is True:
        if profile.is_student:
            score += 10
            reasons.append("学生向けの条件を満たしています")
        else:
            failed_required_conditions.append("学生向けの制度です")

    # 子ども条件 (10点)
    if condition.requires_children is True:
        if profile.has_children:
            score += 10
            reasons.append("子どもがいる世帯向けの条件を満たしています")
        else:
            failed_required_conditions.append("子どもがいる世帯向けの制度です")

    # ひとり親条件 (5点)
    if condition.requires_single_parent is True:
        if profile.is_single_parent:
            score += 5
            reasons.append("ひとり親家庭の条件を満たしています")
        else:
            failed_required_conditions.append("ひとり親家庭向けの制度です")

    # 障害条件 (5点)
    if condition.requires_disabled is True:
        if profile.is_disabled:
            score += 5
            reasons.append("障害をお持ちの方の条件を満たしています")
        else:
            failed_required_conditions.append("障害をお持ちの方向けの制度です")

    if failed_required_conditions:
        return None

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

# 11. API設計

## プロフィールAPI

### プロフィール取得
```http
GET /profile
```
レスポンス：
```json
{
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
}
```

### プロフィール更新
```http
PUT /profile
```
リクエスト：上記と同じJSON形式

---

## 制度API

### 支援制度一覧取得
```http
GET /programs
```

### 支援制度詳細取得
```http
GET /programs/{program_id}
```

---

## マッチングAPI

### プロフィールに合う制度を取得
```http
GET /matches
```

---

# 12. 最初の実装順序

1.  **FastAPI + SQLite 接続設定**: `core/database.py`
2.  **プロフィール機能の実装**: `models/profile.py`, `routers/profiles.py` (認証なし)
3.  **制度データ機能の実装**: `models/support_program.py`, `routers/programs.py`
4.  **Seedデータの作成**: `seed/seed_programs.py` でテスト用制度を登録
5.  **マッチングロジックの実装**: `services/matching_service.py` (年齢計算、スコア判定)
6.  **マッチングAPIの公開**: `routers/matches.py`

---

# 13. GitHub Issueの切り方 (最新方針)

```text
#1 FastAPI + SQLite の初期セットアップ
#2 user_profiles テーブルの作成とプロフィールAPIの実装
#3 support_programs / conditions テーブル의作成
#4 制度一覧・詳細APIの実装
#5 制度データのシード投入スクリプト作成
#6 マッチングロジック（年齢計算・スコア判定）の実装
#7 マッチング結果取得APIの実装
#8 CORS設定とフロントエンド接続確認
```
