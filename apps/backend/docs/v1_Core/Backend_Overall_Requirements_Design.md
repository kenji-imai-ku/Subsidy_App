# 支援制度マッチングアプリ：バックエンド全体設計・実装方針

## 1. このドキュメントの目的

このドキュメントは、支援制度マッチングアプリのバックエンド全体について、要件、設計方針、API、DB設計、実装順序、担当分担の前提を整理するものである。

既存の `system_design.md` と `backend_Implementation_flow_guide.md`、およびフロントエンドから提示されたプロフィール入力画面の連携仕様を統合し、バックエンド担当者2名が同じ前提で実装できる状態にすることを目的とする。

---

## 2. アプリの目的

自治体や国が提供する補助金・給付金・支援制度は多数存在するが、制度の存在を知らない、条件が分かりにくい、情報が分散しているなどの理由で、本来受け取れる支援を見逃してしまう人が少なくない。

本アプリでは、ユーザーが自身の状況を入力することで、条件に合いそうな支援制度を自動で照合し、対象となる可能性のある制度を分かりやすく提示する。

バックエンドの中心的な役割は、次の一文にまとめられる。

> ユーザープロフィールと、構造化された支援制度条件を照合し、「対象となる可能性のある制度」と「その理由」を返すAPIを作る。

初期段階では、検索エンジンやAIチャットではなく、ルールベースのマッチングAPIとして設計する。

---

## 3. 技術構成

初期プロトタイプでは、以下の構成を採用する。

```text
Frontend: Next.js
  ↓ HTTP / JSON
Backend: FastAPI
  ↓ SQLAlchemy
Database: SQLite
```

### 採用方針

* バックエンドは FastAPI で実装する。
* DB は初期プロトタイプとして SQLite を使用する。
* ORM として SQLAlchemy を使用する。
* リクエスト・レスポンスの型定義には Pydantic を使用する。
* ユーザー認証・ログイン機能は実装しない。
* LINE通知、AIチャット、制度情報の自動収集は後回しにする。

---

## 4. バックエンドの責務

バックエンドの責務は大きく3つである。

```text
1. プロフィール管理
2. 支援制度データ管理
3. プロフィールと支援制度条件のマッチング
```

### 4.1 プロフィール管理

フロントエンドのプロフィール入力画面から送信された情報を受け取り、DBに保存する。

主な処理は以下である。

* プロフィール登録・更新
* プロフィール取得
* フロント入力値から内部判定用フィールドへの変換

### 4.2 支援制度データ管理

支援制度の一覧・詳細を取得できるようにする。

初期段階では、制度データは手入力または seed スクリプトで登録する。

主な処理は以下である。

* 支援制度一覧取得
* 支援制度詳細取得
* 支援制度条件の保持
* seed データ投入

### 4.3 マッチング処理

保存されたプロフィールと支援制度条件を照合し、対象となる可能性のある制度を返す。

主な処理は以下である。

* 年齢計算
* 地域条件の判定
* 所得条件の判定
* 世帯条件の判定
* 非課税世帯条件の判定
* マッチ理由・注意事項・スコアの生成

---

## 5. MVPで作る機能

最初に作る範囲は以下に限定する。

### プロフィール系

* プロフィール登録・更新
* プロフィール取得
* フロントエンドの入力仕様に対応したAPI

### 支援制度系

* 支援制度一覧取得
* 支援制度詳細取得
* 開発用 seed データ登録

### マッチング系

* 保存済みプロフィールに合う制度一覧取得
* 各制度について「対象となる可能性がある理由」を返す
* 追加確認が必要な項目を返す
* マッチ度スコアを返す

---

## 6. 後回しにする機能

以下は初期実装では扱わない。

* ユーザー登録・ログイン
* 複数ユーザー管理
* LINE通知
* AIチャット
* 制度情報の自動スクレイピング
* 全国自治体対応
* 管理画面の本格実装
* 申請書類の自動作成

---

## 7. フォルダ構成

基本構成は以下とする。

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
│   │   └── support_program.py
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
├── tests/
├── .env
├── requirements.txt
└── README.md
```

### 各ディレクトリの役割

```text
routers/
APIの入口。URLごとの処理を書く。

schemas/
リクエスト・レスポンスの型を書く。Pydantic。

models/
DBのテーブル定義を書く。SQLAlchemy。

services/
アプリ固有の処理を書く。マッチング処理はここに置く。

repositories/
DBアクセス処理を書く。

core/
DB接続、設定、共通処理を書く。

seed/
開発用の初期データ投入処理を書く。
```

---

## 8. フロントエンド連携方針

フロントエンドからは、現時点で以下の `FormData` が送信される想定である。

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

バックエンドでは、フロントエンドの入力値をそのまま受け取る `ProfileCreateRequest` を用意し、DB保存時に内部判定用の値へ変換する。

### 8.1 バックエンド側で決める方針

#### 生年月日

フロントエンドからは当面 `birthYear`, `birthMonth`, `birthDay` の3項目で受け取る。

バックエンド側で `YYYY-MM-DD` の `birth_date` に変換して保存する。

理由は以下である。

* フロント側の実装を大きく変えなくてよい。
* DB上では日付型として扱える。
* 年齢計算がしやすい。

#### childrenCount

フロントエンドからは文字列で届く可能性があるが、バックエンド側で `int` に変換する。

DBには `children_count` として整数で保存する。

#### householdIncome

フロントエンドからは「200万円未満」などのラベルで届く。

バックエンドでは、マッチング用に概算の上限値 `annual_income_max` へ変換して保存する。

例：

| フロント入力          |  内部保存値の例 |
| --------------- | -------: |
| 200万円未満         |  2000000 |
| 200万円〜400万円未満   |  4000000 |
| 400万円〜600万円未満   |  6000000 |
| 600万円〜800万円未満   |  8000000 |
| 800万円〜1,000万円未満 | 10000000 |
| 1,000万円以上       |     null |

`1,000万円以上` は上限不明として `null` にする。

#### taxExempt

フロントエンドからは「はい」「いいえ」「わからない」が届く。

バックエンドでは、以下のように変換する。

| フロント入力 | 内部保存値 |
| ------ | ----- |
| はい     | true  |
| いいえ    | false |
| わからない  | null  |

`null` の場合は、マッチング結果で「非課税世帯か確認が必要です」と表示する。

#### familyType

フロントエンドからは「独身」「配偶者あり」「ひとり親」「その他」が届く。

バックエンドでは、判定用に以下の値へ変換する。

| フロント入力 | has_spouse | is_single_parent |
| ------ | ---------: | ---------------: |
| 独身     |      false |            false |
| 配偶者あり  |       true |            false |
| ひとり親   |      false |             true |
| その他    |       null |             null |

#### gender

フロントエンド表示値をそのまま保存してもよいが、内部では英語のコード値に変換する方が扱いやすい。

| フロント入力 | 内部値       |
| ------ | --------- |
| 男性     | male      |
| 女性     | female    |
| その他    | other     |
| 回答しない  | no_answer |

---

## 9. DB設計

## 9.1 user_profiles テーブル

プロフィール情報を保存するテーブルである。

認証なしのMVPでは、基本的に最新の1件を使う方針でよい。

```sql
user_profiles
```

| カラム                     | 型              |  必須 | 説明                                        |
| ----------------------- | -------------- | --: | ----------------------------------------- |
| id                      | integer        | yes | プロフィールID                                  |
| name                    | varchar        | yes | ユーザー名                                     |
| prefecture              | varchar        | yes | 都道府県                                      |
| birth_date              | date           | yes | 生年月日                                      |
| gender                  | varchar        | yes | `male` / `female` / `other` / `no_answer` |
| household_income_label  | varchar        | yes | フロントから受け取った所得帯ラベル                         |
| annual_income_max       | integer / null |  no | 所得帯から変換した上限値                              |
| family_type             | varchar        | yes | フロントから受け取った世帯区分                           |
| has_spouse              | boolean / null |  no | 配偶者の有無                                    |
| children_count          | integer        |  no | 子どもの人数。未入力時は0扱い                           |
| has_children            | boolean        | yes | 子どもがいるか                                   |
| is_single_parent        | boolean / null |  no | ひとり親か                                     |
| is_tax_exempt_household | boolean / null |  no | 非課税世帯か                                    |
| created_at              | datetime       | yes | 作成日時                                      |
| updated_at              | datetime       |  no | 更新日時                                      |

### 既存設計から削る、または後回しにする項目

既存設計には以下の項目が含まれていたが、フロント入力仕様に存在しないため、MVPでは後回しにする。

* city
* ward
* employment_status
* is_student
* is_disabled

ただし、支援制度の対象地域が市区町村単位になる可能性は高いため、将来的には `city` と `ward` を追加する余地を残す。

---

## 9.2 support_programs テーブル

支援制度そのものの情報を保存する。

```sql
support_programs
```

| カラム                | 型        |  必須 | 説明                |
| ------------------ | -------- | --: | ----------------- |
| id                 | integer  | yes | 制度ID              |
| title              | varchar  | yes | 制度名               |
| provider           | varchar  | yes | 実施主体              |
| summary            | text     | yes | 概要                |
| benefit            | text     |  no | 支援内容              |
| category           | varchar  |  no | カテゴリ              |
| target_prefecture  | varchar  |  no | 対象都道府県            |
| target_city        | varchar  |  no | 対象市区町村。MVPではnull可 |
| target_ward        | varchar  |  no | 対象区。MVPではnull可    |
| application_url    | text     |  no | 申請先URL            |
| deadline           | date     |  no | 締切                |
| required_documents | text     |  no | 必要書類              |
| source_url         | text     |  no | 情報源URL            |
| is_active          | boolean  | yes | 掲載中か              |
| created_at         | datetime | yes | 作成日時              |
| updated_at         | datetime |  no | 更新日時              |

---

## 9.3 support_program_conditions テーブル

支援制度の条件を機械的に判定しやすい形で保存する。

```sql
support_program_conditions
```

| カラム                    | 型              |  必須 | 説明             |
| ---------------------- | -------------- | --: | -------------- |
| id                     | integer        | yes | 条件ID           |
| program_id             | integer        | yes | 制度ID           |
| min_age                | integer / null |  no | 最低年齢           |
| max_age                | integer / null |  no | 最高年齢           |
| max_annual_income      | integer / null |  no | 年収上限           |
| requires_tax_exempt    | boolean / null |  no | 非課税世帯である必要があるか |
| requires_children      | boolean / null |  no | 子どもが必要か        |
| min_children_count     | integer / null |  no | 最低子ども人数        |
| requires_single_parent | boolean / null |  no | ひとり親である必要があるか  |
| required_gender        | varchar / null |  no | 対象性別           |
| condition_description  | text           |  no | 人間向け条件説明       |

### MVPでは扱わない条件

既存設計には以下の条件があったが、フロント入力仕様にないためMVPでは原則使用しない。

* requires_student
* requires_unemployed
* requires_disabled

---

## 10. API設計

## 10.1 ヘルスチェック

```http
GET /health
```

レスポンス例：

```json
{
  "status": "ok"
}
```

---

## 10.2 プロフィール取得

```http
GET /profile
```

レスポンス例：

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

---

## 10.3 プロフィール登録・更新

```http
PUT /profile
```

リクエスト例：

```json
{
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
}
```

レスポンス例：

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

---

## 10.4 支援制度一覧取得

```http
GET /programs
```

クエリパラメータは任意で追加する。

```http
GET /programs?category=housing&prefecture=京都府
```

レスポンス例：

```json
[
  {
    "id": 1,
    "title": "住居確保給付金",
    "provider": "京都市",
    "summary": "離職等により住居を失うおそれがある方に家賃相当額を支給する制度です。",
    "benefit": "家賃相当額を一定期間支給",
    "category": "housing",
    "targetPrefecture": "京都府",
    "targetCity": "京都市",
    "targetWard": null,
    "applicationUrl": "https://example.com",
    "deadline": null
  }
]
```

---

## 10.5 支援制度詳細取得

```http
GET /programs/{program_id}
```

レスポンス例：

```json
{
  "id": 1,
  "title": "住居確保給付金",
  "provider": "京都市",
  "summary": "離職等により住居を失うおそれがある方に家賃相当額を支給する制度です。",
  "benefit": "家賃相当額を一定期間支給",
  "category": "housing",
  "targetPrefecture": "京都府",
  "targetCity": "京都市",
  "targetWard": null,
  "applicationUrl": "https://example.com",
  "requiredDocuments": "本人確認書類、収入確認書類など",
  "sourceUrl": "https://example.com/source",
  "conditionDescription": "収入が一定額以下であること等"
}
```

---

## 10.6 マッチング結果取得

```http
GET /matches
```

保存済みプロフィールをもとに、対象となる可能性のある支援制度を返す。

レスポンス例：

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
      "applicationUrl": "https://example.com"
    },
    "score": 75,
    "status": "possible",
    "reasons": [
      "居住地が対象都道府県に含まれています",
      "年齢条件を満たしている可能性があります"
    ],
    "warnings": [
      "詳細な所得条件は公式情報を確認してください"
    ]
  }
]
```

### status の意味

| status   | 意味                    |
| -------- | --------------------- |
| eligible | 入力情報上、条件を満たしている可能性が高い |
| possible | 一部確認が必要だが、対象となる可能性がある |

明確に対象外と判定した制度は、MVPではレスポンスに含めない。

---

## 11. マッチングロジック設計

初期実装では、ルールベースでスコアを計算する。

### スコア例

合計100点満点を目安とする。

```text
地域一致: 30点
年齢条件: 20点
所得・税条件: 30点
世帯条件: 20点
```

### 判定の考え方

* 明確に必須条件を満たさない場合は対象外とする。
* 入力が `null` または「わからない」の場合は対象外にせず、`warnings` に追加する。
* 条件を満たした場合は `reasons` に理由を追加する。
* 最終的に、警告がなければ `eligible`、警告があれば `possible` とする。

---

## 12. 実装順序

2人で分担する場合でも、最初に共通基盤とAPI仕様を揃える必要がある。

### Step 0: 共通作業

* ブランチ運用を決める。
* FastAPIの起動確認を行う。
* SQLite接続を設定する。
* CORS設定を行う。
* DB作成方法を決める。
* APIのURL・リクエスト・レスポンス形式を固定する。

### Step 1: 担当A プロフィール機能

* `user_profiles` モデル作成
* `ProfileRequest` / `ProfileResponse` 作成
* 入力値変換処理作成
* `PUT /profile` 実装
* `GET /profile` 実装

### Step 2: 担当B 支援制度機能

* `support_programs` モデル作成
* `support_program_conditions` モデル作成
* `ProgramResponse` 作成
* `GET /programs` 実装
* `GET /programs/{program_id}` 実装
* seed データ作成

### Step 3: 担当B中心・A確認 マッチング機能

* `matching_service.py` 作成
* 年齢計算実装
* 条件判定実装
* `GET /matches` 実装
* フロントと接続確認

---

## 13. 役割分担に関する注意点

提示されている役割分担は、大枠としては妥当である。

```text
担当A：プロフィール機能の垂直実装
担当B：支援制度・マッチング機能の垂直実装
```

ただし、以下の点に注意が必要である。

### 13.1 マッチング機能はプロフィール仕様に依存する

担当Bのマッチング処理は、担当Aが作るプロフィールのDB項目・レスポンス形式に強く依存する。

そのため、実装前に以下を固定しておく必要がある。

* `birth_date` の保存形式
* `annual_income_max` の意味
* `children_count` の扱い
* `is_tax_exempt_household` の `true / false / null` の意味
* `family_type` から派生する `has_spouse` / `is_single_parent` の意味

### 13.2 共通ファイルの編集衝突に注意する

以下のファイルは両者が触りやすいため、担当を明確にする。

| ファイル                             | 主担当                 |
| -------------------------------- | ------------------- |
| `app/main.py`                    | 最初に共通で作成。その後は変更者を相談 |
| `app/core/database.py`           | 共通基盤担当、または先に作る人     |
| `app/models/profile.py`          | 担当A                 |
| `app/models/support_program.py`  | 担当B                 |
| `app/schemas/profile.py`         | 担当A                 |
| `app/schemas/support_program.py` | 担当B                 |
| `app/schemas/match.py`           | 担当B。ただし担当Aが確認       |
| `app/routers/profiles.py`        | 担当A                 |
| `app/routers/programs.py`        | 担当B                 |
| `app/routers/matches.py`         | 担当B                 |

### 13.3 最初にAPI契約だけ決める

実装を分ける前に、最低限以下をチームで合意する。

* `PUT /profile` のリクエスト形式
* `GET /profile` のレスポンス形式
* `GET /matches` のレスポンス形式
* プロフィール未登録時の挙動
* seed データの投入方法

---

## 14. GitHub Issue案

```text
#1 FastAPI + SQLite の初期セットアップ
#2 CORS設定と /health API の作成
#3 user_profiles テーブルの作成
#4 プロフィール入力値の変換処理を実装
#5 PUT /profile API の実装
#6 GET /profile API の実装
#7 support_programs / support_program_conditions テーブルの作成
#8 支援制度 seed データの作成
#9 GET /programs API の実装
#10 GET /programs/{program_id} API の実装
#11 マッチングロジックの実装
#12 GET /matches API の実装
#13 フロントエンドとの接続確認
```

---

## 15. 完了条件

MVPのバックエンドとして、以下ができれば完了とする。

* FastAPIが起動する。
* SQLiteに接続できる。
* フロントのプロフィール入力データを `PUT /profile` で保存できる。
* `GET /profile` で保存済みプロフィールを取得できる。
* seed データとして支援制度を数件登録できる。
* `GET /programs` で制度一覧を取得できる。
* `GET /programs/{program_id}` で制度詳細を取得できる。
* `GET /matches` でプロフィールに合いそうな制度を取得できる。
* マッチング結果に、スコア、理由、注意事項が含まれている。
