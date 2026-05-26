# v2_Applied_1_latest バックエンド拡張ドキュメント一式

本ドキュメントは、支援制度マッチングアプリのMVP実装を拡張するための実装指示書である。

以下の3つのドキュメントをこの順番で読むこと。

1. `01_Backend_Extension_Overall_Design.md`
   今回の追加実装全体に関する共通設計・固定事項・実装方針
2. `02_Backend_RoleA_User_Profile_Status_Implementation.md`
   担当A：プロフィール・ユーザー状態管理の実装指示
3. `03_Backend_RoleB_Program_Data_Implementation.md`
   担当B：支援制度データ・制度管理の実装指示

---

# 01_Backend_Extension_Overall_Design.md

# 支援制度マッチングアプリ v2_Applied_1_latest：バックエンド拡張全体設計

## 1. このドキュメントの目的

このドキュメントは、既存MVPバックエンドを拡張するための共通設計・固定事項・実装方針を整理するものである。

今回の拡張では、マッチングロジックの高度化は主目的としない。マッチングロジックは後続で別途設計・実装する予定である。

今回の主目的は、後からマッチングロジックを拡張しやすいように、以下を整備することである。

- ユーザー側のプロフィール情報を拡張する
- 支援制度側のデータ構造を拡張する
- 制度情報をより現実の支援制度に近い形で表現できるようにする
- ユーザーが制度を「気になる」「確認中」「申請済み」などとして管理できるようにする
- seedデータや開発用APIを整備し、制度データを増やしやすくする

## 2. 今回の拡張の位置づけ

既存MVPでは、以下の3機能が中心である。

- プロフィール管理
- 支援制度データ管理
- プロフィールと支援制度条件のマッチング

今回のv2拡張では、このうち主に以下を拡張する。

- プロフィール管理
- 支援制度データ管理
- ユーザーごとの制度管理状態

一方で、以下は今回の主対象外とする。

- マッチングロジックの本格改良
- Webスクレイピングの本実装
- メール通知
- LINE通知
- ユーザー認証・ログイン
- 管理画面の本格実装
- 申請書類の自動生成

## 3. 技術構成

既存MVPの技術構成を維持する。

```text
Frontend: Next.js
  ↓ HTTP / JSON
Backend: FastAPI
  ↓ SQLAlchemy
Database: SQLite
```

実装方針は以下とする。

- バックエンドは FastAPI を使用する
- ORM は SQLAlchemy を使用する
- リクエスト・レスポンスの型定義には Pydantic を使用する
- DB は初期プロトタイプとして SQLite を使用する
- 認証・ログインは実装しない
- 既存APIとの互換性をできる限り維持する

## 4. 役割分担

今回の実装は、担当Aと担当Bで以下のように分担する。

### 担当A：ユーザー側担当

担当Aは、ユーザーに関する情報を扱う。

主な担当範囲は以下である。

- `user_profiles` の拡張
- `profile_employment_statuses` の追加
- `profile_special_conditions` の追加
- `PUT /profile` の拡張
- `GET /profile` の拡張
- `user_program_statuses` の追加
- `GET /program-statuses` の追加
- `PUT /program-statuses/{program_id}` の追加

担当Aは、後続のマッチングロジックが参照する「ユーザー側の判定材料」を整備する。

### 担当B：制度側担当

担当Bは、支援制度そのものと制度条件を扱う。

主な担当範囲は以下である。

- `support_programs` の拡張
- `support_program_conditions` の拡張
- `program_sources` の追加
- `program_required_documents` の追加、ただし後回し可
- `GET /programs` の絞り込み条件追加
- `GET /programs/{program_id}` のレスポンス拡張
- seedデータの拡張
- `POST /dev/seed/programs` の追加
- `POST /dev/programs` の追加
- `PUT /dev/programs/{program_id}` の追加

担当Bは、後続のマッチングロジックが参照する「制度側の判定材料」を整備する。

## 5. マッチングロジックとの関係

今回のv2拡張では、マッチングロジックの大幅な改良は行わない。

ただし、後続でマッチングロジックを拡張しやすいように、以下のテーブル構造を整備する。

```text
ユーザー側
- user_profiles
- profile_employment_statuses
- profile_special_conditions

制度側
- support_programs
- support_program_conditions

ユーザーの制度管理状態
- user_program_statuses
```

後続のマッチングロジックは、基本的に以下のように実装される想定である。

```text
user_profiles
profile_employment_statuses
profile_special_conditions
        ↓
matching_service.py
        ↑
support_programs
support_program_conditions
```

今回の実装では、既存の `matching_service.py` が存在する場合、必要最低限の互換性維持にとどめる。

新しく追加するプロフィール項目・制度条件項目を既存マッチングにすべて反映する必要はない。

ただし、以下のTODOコメントを残しておくこと。

```python
# TODO(v2 matching):
# v2で追加された profile_employment_statuses,
# profile_special_conditions,
# support_program_conditions の拡張項目を使って、
# マッチング条件を段階的に追加する。
```

## 6. DBマイグレーション方針

既存MVPがSQLiteで動作している前提で、以下の方針を採用する。

### 6.1 開発段階ではDB再作成を許容する

今回のプロジェクトはMVP拡張段階であり、本番データを保持する必要がない想定である。

そのため、開発環境では以下を許容する。

- 既存SQLiteファイルの削除
- テーブル再作成
- seedデータの再投入

ただし、既存実装が `Base.metadata.create_all()` でテーブル作成している場合は、その方式に合わせる。

Alembicを導入済みでない場合、今回の拡張で無理にAlembicを導入しない。

### 6.2 実装時の注意

- 既存テーブル名はできる限り変更しない
- 既存APIのエンドポイント名はできる限り変更しない
- 既存カラムを削除する場合は慎重に行う
- 既存フロントが送るリクエストは引き続き受け取れるようにする
- 追加項目は原則optionalにして、既存フロントとの互換性を保つ

## 7. 命名規則

### 7.1 Python / DB

Pythonコード、SQLAlchemyモデル、DBカラムでは snake_case を使用する。

例：

```python
is_tax_exempt_household
employment_status
support_type
application_required
```

### 7.2 API JSON

フロントエンド向けJSONでは camelCase を使用する。

例：

```json
{
  "isTaxExemptHousehold": true,
  "employmentStatus": "student",
  "supportType": "cash",
  "applicationRequired": true
}
```

### 7.3 Pydantic schema

Pydantic schemaでは、既存実装の方針を優先する。

既存が camelCase のフィールド名を直接使っている場合は、それに合わせる。

既存が snake_case + alias を使っている場合は、それに合わせる。

重要なのは、APIレスポンスがフロント側で扱いやすい camelCase になることである。

## 8. null / unknown / false の扱い

今回の拡張では、以下の区別を必ず守る。

```text
true       明確に「はい」
false      明確に「いいえ」
null       未入力・不明・まだ確認していない
unknown    選択肢として「わからない」を保存したい場合のコード値
```

### 8.1 boolean項目

boolean項目は原則として以下の3値を許容する。

```text
true / false / null
```

例：

```text
is_unemployed
is_job_seeking
has_health_insurance
is_pregnant
has_disability
```

### 8.2 enum項目

enum項目では、必要に応じて `unknown` を許容する。

例：

```text
employment_status = unknown
application_method = unknown
```

### 8.3 マッチング上の扱い

今回の実装では高度なマッチングは行わないが、後続実装では以下の方針とする。

- `false` は明確な否定として扱う
- `null` は未入力・不明として扱い、対象外判定に直結させない
- `unknown` はユーザーが「わからない」を選んだ状態として扱い、確認事項に出す

## 9. 固定するEnum値

担当A・担当Bで値の不一致が起こらないよう、以下のEnum値を固定する。

### 9.1 gender

```text
male
female
other
no_answer
```

### 9.2 employment_status

```text
employed
unemployed
student
self_employed
part_time
homemaker
retired
other
unknown
```

### 9.3 income_decreased_reason

```text
job_loss
business_closure
reduced_shift
income_drop
leave_absence
other
unknown
```

### 9.4 savings_amount_range

```text
under_500k
500k_to_1m
1m_to_3m
3m_to_5m
5m_or_more
unknown
```

### 9.5 disability_type

```text
physical
intellectual
mental
intractable_disease
other
unknown
```

### 9.6 support_type

```text
cash
subsidy
medical
service_discount
service_dispatch
loan
goods
consultation
tax_reduction
other
```

### 9.7 benefit_amount_type

```text
fixed
max_amount
depends
free_text
unknown
```

### 9.8 benefit_unit

```text
per_person
per_child
per_household
per_month
per_use
one_time
other
unknown
```

### 9.9 application_method

```text
online
mail
counter
automatic
not_required
unknown
```

### 9.10 application_period_type

```text
always
deadline
limited
unknown
```

### 9.11 confidence_level

```text
official
manual_checked
estimated
dummy
```

### 9.12 source_type

```text
html
pdf
manual
other
```

### 9.13 user_program_status

```text
interested
checking
applied
approved
rejected
not_applicable
```

### 9.14 housing_status

```text
owned
rented
public_housing
living_with_family
other
unknown
```

### 9.14 housing_status

```text
owned
rented
public_housing
living_with_family
other
unknown
```

## 10. 今回追加・拡張するテーブル一覧

今回の拡張後、主要テーブルは以下となる。

```text
ユーザー側
- user_profiles
- profile_employment_statuses
- profile_special_conditions
- user_program_statuses (last_viewed_at は PUT 時のみ更新)

制度側
- support_programs
- support_program_conditions
- program_sources
- program_required_documents  ※後回し可
```

## 11. 既存APIとの互換性

既存MVPで以下のAPIがある前提とする。

```text
GET /health
GET /profile
PUT /profile
GET /programs
GET /programs/{program_id}
GET /matches
```

今回の実装では、上記APIを削除しない。

プロフィール拡張・制度拡張によりレスポンス項目は増えてよいが、既存項目は可能な限り維持する。

## 12. 今回追加するAPI一覧

### 担当A

```text
GET /program-statuses
PUT /program-statuses/{program_id}
```

### 担当B

```text
POST /dev/seed/programs
POST /dev/programs
PUT /dev/programs/{program_id}
```

`DELETE /dev/programs/{program_id}` は必須ではない。時間があれば実装する。

## 13. エラーハンドリング共通方針

### 13.1 プロフィール未登録

`GET /profile` でプロフィールが存在しない場合、既存実装に合わせる。

特に方針がない場合は、以下を採用する。

```http
404 Not Found
```

レスポンス例：

```json
{
  "detail": "Profile not found"
}
```

### 13.2 program_id が存在しない

制度IDが存在しない場合は以下を返す。

```http
404 Not Found
```

レスポンス例：

```json
{
  "detail": "Program not found"
}
```

### 13.3 validation error

FastAPI / Pydantic 標準の422エラーを使用してよい。

### 13.4 dev API

`/dev/*` APIは開発用である。

認証は実装しないが、フロント本番導線から直接使用しない想定である。

## 14. 実装順序

2人で並行実装する場合の推奨順序は以下である。

### Step 0：共通確認

- 本ドキュメントを確認する
- Enum値を固定する
- DB再作成方針を確認する
- 既存APIを削除しないことを確認する

### Step 1：担当A・Bがそれぞれモデルを拡張

担当A：

- `user_profiles` の拡張
- `profile_employment_statuses` 追加
- `profile_special_conditions` 追加
- `user_program_statuses` 追加

担当B：

- `support_programs` 拡張
- `support_program_conditions` 拡張
- `program_sources` 追加
- `program_required_documents` 追加、または後回し

### Step 2：API schemaの拡張

担当A：プロフィール・ユーザー制度状態のschema

担当B：制度・制度条件・情報源のschema

### Step 3：repository / service / router の実装

担当A：プロフィール・ユーザー制度状態

担当B：制度一覧・詳細・dev API・seed

### Step 4：動作確認

- FastAPIが起動する
- DBが作成される
- seedデータを投入できる
- `GET /profile`, `PUT /profile` が動く
- `GET /programs`, `GET /programs/{program_id}` が動く
- `GET /program-statuses`, `PUT /program-statuses/{program_id}` が動く
- 既存の `GET /matches` が壊れていない

## 15. 後続マッチング実装に備えた固定事項

今回のv2拡張では、マッチングロジックの本格改良は行わない。

ただし、後続でマッチングロジックを実装・改良するAIエージェントが迷わないように、以下の事項をこの段階で固定する。

### 15.1 マッチングロジックの配置場所

マッチングに関する判定ロジックは、原則として以下に集約する。

```text
app/services/matching_service.py
```

以下の場所に、複雑なマッチング判定を分散して書いてはいけない。

```text
routers/
schemas/
repositories/
models/
```

各層の責務は以下とする。

```text
routers/       APIの入口。リクエストを受け取り、serviceを呼び出す。
schemas/       リクエスト・レスポンスの型定義を行う。
repositories/  DBアクセスのみを行う。
models/        DBテーブル定義のみを行う。
services/      アプリ固有の処理・判定ロジックを行う。
```

### 15.2 後続マッチングが参照するテーブル

後続のマッチングロジックは、基本的に以下のテーブルを参照する。

```text
ユーザー側
- user_profiles
- profile_employment_statuses
- profile_special_conditions

制度側
- support_programs
- support_program_conditions
```

`user_program_statuses` は、ユーザーが制度をどう管理しているかを表すテーブルであり、制度の対象判定そのものには原則使用しない。

ただし、将来的に「申請済みの制度を除外する」「お気に入りを優先表示する」などの表示制御に使ってもよい。

### 15.3 GET /matches の互換性

既存MVPの `GET /matches` は削除しない。

今回のv2実装で、`GET /matches` の中身を無理に高度化する必要はない。

今回の段階では、以下のどちらかを満たせばよい。

```text
A. 既存の /matches が従来通り動作する
B. v2のDB変更に合わせて最低限修正し、起動不能・実行不能にならない
```

新しいプロフィール項目や制度条件項目を、今回の時点ですべてマッチング判定に反映する必要はない。

### 15.4 後続マッチングで追加予定のレスポンス項目

既存のマッチングレスポンスは、以下の形を基本とする。

```json
{
  "program": {},
  "score": 75,
  "status": "possible",
  "reasons": [],
  "warnings": []
}
```

後続のマッチングロジックでは、必要に応じて以下を追加する余地を残す。

```json
{
  "missingInformation": [],
  "manualCheckRequired": true,
  "matchedConditionKeys": [],
  "unmatchedConditionKeys": []
}
```

今回のv2実装では、上記項目を必ず実装する必要はない。

ただし、後続で追加しやすいように、schemaを過度に固定しすぎないこと。

### 15.5 status の将来方針

後続マッチングでは、status は以下の値を想定する。

```text
eligible        入力情報上、条件を満たしている可能性が高い
possible        一部確認が必要だが、対象となる可能性がある
not_applicable  明確に対象外
```

既存MVPでは、明確に対象外の制度をレスポンスに含めない方針でもよい。

後続実装で `not_applicable` を返すかどうかは、マッチング設計ドキュメントで改めて決める。

### 15.6 null / unknown のマッチング上の意味

後続マッチングでは、以下の扱いを基本とする。

```text
true       条件を明確に満たす、または該当する
false      条件を明確に満たさない、または該当しない
null       未入力・未確認なので、原則として即対象外にはしない
unknown    ユーザーが「わからない」と答えた状態。確認事項に出す
```

今回のv2実装では、この意味が崩れないようにDBへ保存すること。

## 16. 既存 /matches を壊さないための注意

今回のv2拡張では、プロフィール・制度条件のテーブル構造が拡張されるため、既存の `matching_service.py` が古いカラムだけを前提としている場合がある。

その場合でも、以下を守ること。

### 16.1 既存カラムを不用意に削除しない

既存マッチングが参照している可能性のある以下のカラムは、原則として削除しない。

```text
user_profiles.birth_date
user_profiles.gender
user_profiles.annual_income_max
user_profiles.children_count
user_profiles.has_children
user_profiles.is_single_parent
user_profiles.is_tax_exempt_household

support_programs.id
support_programs.title
support_programs.provider
support_programs.summary
support_programs.benefit
support_programs.category
support_programs.target_prefecture
support_programs.target_city
support_programs.target_ward
support_programs.application_url
support_programs.deadline
support_programs.is_active

support_program_conditions.min_age
support_program_conditions.max_age
support_program_conditions.max_annual_income
support_program_conditions.requires_tax_exempt
support_program_conditions.requires_children
support_program_conditions.min_children_count
support_program_conditions.requires_single_parent
support_program_conditions.required_gender
support_program_conditions.condition_description
```

### 16.2 既存schemaを壊さない

既存フロントが受け取っている可能性のあるレスポンス項目は、可能な限り維持する。

項目を増やすのはよいが、既存項目の名前を変更しない。

避けるべき例：

```text
applicationUrl を application_url に変える
supportType を support_type に変える
birthDate を birth_date に変える
```

API JSONでは camelCase を維持する。

### 16.3 /matches の暫定対応

v2追加項目に対応しきれない場合、`matching_service.py` には以下のようなTODOを残す。

```python
# TODO(v2 matching):
# v2で追加された profile_employment_statuses,
# profile_special_conditions,
# support_program_conditions の拡張項目を使って、
# マッチング条件を段階的に追加する。
```

ただし、TODOを残すだけでなく、既存の `/matches` がエラーにならないことは必ず確認する。

### 16.4 relationship追加時の注意

SQLAlchemyでrelationshipを追加する場合、既存クエリが壊れないようにする。

特に、1対1の関係である以下は、関連レコードが存在しない場合でもアプリが落ちないようにする。

```text
UserProfile.employment_status
UserProfile.special_conditions
```

関連レコードがない場合は `None` として扱い、APIレスポンスでは `null` または空のオブジェクトに変換する。

## 17. DB再作成・seed再投入の手順

今回のプロジェクトはMVP拡張段階であり、開発環境ではDB再作成を許容する。

ただし、AIエージェントが勝手に手順を変えないよう、以下を標準手順とする。

### 17.1 Alembicを使っていない場合

既存実装が `Base.metadata.create_all()` によるテーブル作成である場合、以下の方針とする。

```text
1. アプリを停止する
2. 既存のSQLite DBファイルを削除する
3. 担当A・担当Bの両方のモデル拡張が完了し、__init__.py 等に登録されていることを確認する（同期確認）
4. FastAPI起動時、または初期化処理でテーブルを再作成する。この際、全テーブルが作成対象に含まれていることをログ等で確認する。
5. POST /dev/seed/programs または seed スクリプトで制度データを投入する
6. PUT /profile でプロフィールを再登録する
```

DBファイル名・配置場所は既存実装に従う。

AIエージェントは、DBファイルの場所を推測で変更してはいけない。

### 17.2 Alembicを導入済みの場合

既存実装にAlembicが導入されている場合は、既存方針に従う。

ただし、今回の拡張のためだけに新規でAlembicを導入する必要はない。

### 17.3 seed再投入の注意

seedデータを再投入する場合、同じ制度が重複登録されないようにする。

最低限、以下のどちらかの対応を行う。

```text
A. title + provider の組み合わせで既存確認し、存在すれば追加しない
B. 開発用seedデータを削除してから再投入する
```

推奨は A である。

ただし、開発初期でDB再作成する場合は B でもよい。

## 18. A/B共通の実装チェックリスト

担当A・担当Bは、それぞれの実装完了後、以下を確認する。

### 18.1 起動確認

```text
- FastAPIが起動する
- import error が出ない
- SQLAlchemy model の定義エラーが出ない
- DBテーブルが作成される
```

### 18.2 既存API確認

```text
GET /health
GET /profile
PUT /profile
GET /programs
GET /programs/{program_id}
GET /matches
```

上記APIが削除されていないことを確認する。

`GET /matches` は、マッチング精度が未改善でもよいが、サーバーエラーにならないこと。

### 18.3 新規API確認

担当A：

```text
GET /program-statuses
PUT /program-statuses/{program_id}
```

担当B：

```text
POST /dev/seed/programs
POST /dev/programs
PUT /dev/programs/{program_id}
```

### 18.4 データ確認

```text
- プロフィール拡張項目が保存される
- employment情報が保存される
- specialConditions情報が保存される
- support_type が保存される
- application_required が保存される
- program_sources が保存される
- user_program_statuses が重複せずに保存される
```

### 18.5 JSON命名確認

APIレスポンスがフロント向けに camelCase になっていることを確認する。

DB内部やPython内部は snake_case でよい。

## 19. AIエージェント向け実装時の禁止事項

AIエージェントに実装させる場合、以下を禁止する。

### 19.1 既存APIの削除禁止

以下のAPIを削除してはいけない。

```text
GET /health
GET /profile
PUT /profile
GET /programs
GET /programs/{program_id}
GET /matches
```

### 19.2 勝手な認証導入禁止

今回のv2拡張では、認証・ログインを実装しない。

以下を勝手に追加してはいけない。

```text
JWT認証
OAuth
ユーザー登録
ログインAPI
パスワード管理
```

### 19.3 技術構成の変更禁止

今回の実装で、以下を勝手に変更してはいけない。

```text
SQLite から PostgreSQL への変更
SQLAlchemy から別ORMへの変更
FastAPI から別フレームワークへの変更
Pydantic 以外のschema方式への変更
```

### 19.4 ディレクトリ構成の大幅変更禁止

既存の構成を大幅に変えない。

特に、以下を勝手に行ってはいけない。

```text
app/ 配下を全面的に作り直す
routers / schemas / models / services / repositories の責務を崩す
既存ファイルを無関係にリネームする
```

### 19.5 マッチングロジックの作り込み禁止

今回のv2拡張では、マッチングロジックの本格改良は行わない。

AIエージェントは、今回の担当範囲を超えて、複雑なマッチングロジックを勝手に実装してはいけない。

やってよいのは以下である。

```text
- 既存 /matches が壊れないようにする
- v2追加テーブルにより import error や attribute error が出る場合に最低限修正する
- 後続実装用のTODOコメントを残す
```

### 19.6 フロント仕様を勝手に破壊しない

既存フロントが送るプロフィール入力形式は引き続き受け取れるようにする。

特に、以下の旧形式は受け取れるようにする。

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

### 19.7 Enum値の独自追加禁止

Enum値は本ドキュメントで固定したものを使用する。

必要な値が不足している場合は、勝手に追加せず、まず `other` または `unknown` を使用する。

## 20. 完了条件

今回のv2拡張の完了条件は以下である。

- 既存APIが削除されていない
- プロフィールに市区町村・就労状況・特別条件を保存できる
- 支援制度に支援タイプ・申請方法・情報源を保存できる
- 制度条件に就労・収入減少・妊娠出産・障害・健康保険などの条件を保存できる
- seedデータが複数の制度タイプを含んでいる
- 制度一覧APIでカテゴリ・支援タイプ・地域などで絞り込める
- ユーザーが制度ごとにお気に入り・確認中・申請済みなどの状態を保存できる
- 後続のマッチングロジック実装者が参照すべきテーブルが明確になっている
- 既存の `GET /matches` が起動不能・実行不能になっていない
- AIエージェントが勝手に認証・DB変更・技術構成変更・複雑なマッチング実装を行わないよう、禁止事項が明文化されている
