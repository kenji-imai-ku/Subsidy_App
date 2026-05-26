# 02_Backend_RoleA_User_Profile_Status_Implementation.md

# 担当A 実装指示書：プロフィール・ユーザー状態管理

## 1. 担当Aの目的

担当Aは、ユーザー側の情報を拡張する。

今回の担当Aの目的は、後続のマッチングロジックが利用できるように、ユーザーの生活状況・就労状況・医療/育児/障害等の条件を構造化して保存・取得できるようにすることである。

また、ユーザーが各制度について「気になる」「確認中」「申請済み」などの状態を保存できるようにする。

## 2. 担当Aの実装範囲

担当Aは以下を実装する。

```text
DB / Model
- user_profiles の拡張
- profile_employment_statuses の追加
- profile_special_conditions の追加
- user_program_statuses の追加

Schema
- profile.py の拡張
- user_program_status.py の追加

Repository
- profile_repository.py の拡張
- user_program_status_repository.py の追加

Service
- profile_service.py の拡張
- user_program_status_service.py の追加

Router
- profiles.py の拡張
- program_statuses.py の追加

API
- GET /profile
- PUT /profile
- GET /program-statuses
- PUT /program-statuses/{program_id}
```

## 3. 担当Aが触る主なファイル

既存構成に合わせて、以下のファイルを作成・編集する。

```text
app/models/profile.py
app/models/user_program_status.py

app/schemas/profile.py
app/schemas/user_program_status.py

app/repositories/profile_repository.py
app/repositories/user_program_status_repository.py

app/services/profile_service.py
app/services/user_program_status_service.py

app/routers/profiles.py
app/routers/program_statuses.py

app/main.py  ※router追加時のみ最小限編集
```

`app/main.py` は担当Bも触る可能性があるため、編集はrouter登録など最小限にする。

## 4. DB設計

## 4.1 user_profiles の拡張

既存の `user_profiles` テーブルを拡張する。

既存カラムは可能な限り維持する。

追加後の想定カラムは以下である。

```text
id
name
prefecture
city
ward
birth_date
gender
household_income_label
annual_income_max
monthly_income
savings_amount_range
housing_status
family_type
has_spouse
children_count
has_children
is_single_parent
is_tax_exempt_household
is_household_head
created_at
updated_at
```

### 4.1.1 追加カラム

| カラム                  | 型              | 必須 | 説明                     |
| -------------------- | -------------- | -: | ---------------------- |
| city                 | varchar / null | no | 市区町村。例：京都市             |
| ward                 | varchar / null | no | 区。例：左京区                |
| monthly_income       | integer / null | no | 直近月収。制度条件で月収上限を見る場合に使う |
| savings_amount_range | varchar / null | no | 預貯金帯。Enum値を使用          |
| housing_status       | varchar / null | no | 住居形態。Enum値を使用          |
| is_household_head    | boolean / null | no | 世帯主かどうか                |

### 4.1.2 savings_amount_range の値

以下の値を使用する。

```text
under_500k
500k_to_1m
1m_to_3m
3m_to_5m
5m_or_more
unknown
```

未入力の場合は `null` とする。

「わからない」と明示的に入力された場合は `unknown` とする。

### 4.1.3 housing_status の値

以下の値を使用する。

```text
owned
rented
public_housing
living_with_family
other
unknown
```

未入力の場合は `null` とする。

「わからない」と明示的に入力された場合は `unknown` とする。

## 4.2 profile_employment_statuses テーブル

就労・離職・求職・収入減少に関する情報を保存する。

```text
profile_employment_statuses
```

| カラム                     | 型               |  必須 | 説明                      |
| ----------------------- | --------------- | --: | ----------------------- |
| id                      | integer         | yes | ID                      |
| profile_id              | integer         | yes | user_profiles.id への外部キー |
| employment_status       | varchar / null  |  no | 就労状況                    |
| is_unemployed           | boolean / null  |  no | 離職中か                    |
| unemployed_since        | date / null     |  no | 離職日                     |
| is_job_seeking          | boolean / null  |  no | 求職活動中か                  |
| income_decreased        | boolean / null  |  no | 収入減少があるか                |
| income_decreased_reason | varchar / null  |  no | 収入減少理由                  |
| created_at              | datetime        | yes | 作成日時                    |
| updated_at              | datetime / null |  no | 更新日時                    |

### 4.2.1 employment_status の値

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

### 4.2.2 income_decreased_reason の値

```text
job_loss
business_closure
reduced_shift
income_drop
leave_absence
other
unknown
```

### 4.2.3 関係

`user_profiles` と `profile_employment_statuses` は 1対1 とする。

SQLAlchemyでは、可能であれば relationship を設定する。

```text
UserProfile 1 -- 1 ProfileEmploymentStatus
```

## 4.3 profile_special_conditions テーブル

医療・妊娠出産・障害・介護・ヤングケアラー等に関する情報を保存する。

```text
profile_special_conditions
```

| カラム                          | 型               |  必須 | 説明                      |
| ---------------------------- | --------------- | --: | ----------------------- |
| id                           | integer         | yes | ID                      |
| profile_id                   | integer         | yes | user_profiles.id への外部キー |
| has_health_insurance         | boolean / null  |  no | 健康保険に加入しているか            |
| is_pregnant                  | boolean / null  |  no | 妊娠中か                    |
| postpartum_months            | integer / null  |  no | 産後何か月か                  |
| has_disability               | boolean / null  |  no | 障害があるか                  |
| disability_type              | varchar / null  |  no | 障害種別                    |
| disability_grade             | varchar / null  |  no | 等級等。自由記述                |
| has_medical_care_child       | boolean / null  |  no | 医療的ケア児がいるか              |
| has_care_required_family     | boolean / null  |  no | 介護が必要な家族がいるか            |
| has_young_carer_in_household | boolean / null  |  no | ヤングケアラーに該当する家族がいるか      |
| created_at                   | datetime        | yes | 作成日時                    |
| updated_at                   | datetime / null |  no | 更新日時                    |

### 4.3.1 disability_type の値

```text
physical
intellectual
mental
intractable_disease
other
unknown
```

### 4.3.2 関係

`user_profiles` と `profile_special_conditions` は 1対1 とする。

```text
UserProfile 1 -- 1 ProfileSpecialCondition
```

## 4.4 user_program_statuses テーブル

ユーザーが各制度をどう扱っているかを保存する。

```text
user_program_statuses
```

| カラム            | 型               |  必須 | 説明                         |
| -------------- | --------------- | --: | -------------------------- |
| id             | integer         | yes | ID                         |
| profile_id     | integer         | yes | user_profiles.id への外部キー    |
| program_id     | integer         | yes | support_programs.id への外部キー |
| status         | varchar / null  |  no | 制度に対する状態                   |
| is_favorite    | boolean         | yes | お気に入りか                     |
| memo           | text / null     |  no | ユーザーメモ                     |
| last_viewed_at | datetime / null |  no | 最後に閲覧した日時                  |
| created_at     | datetime        | yes | 作成日時                       |
| updated_at     | datetime / null |  no | 更新日時                       |

### 4.4.1 status の値

```text
interested
checking
applied
approved
rejected
not_applicable
```

### 4.4.2 unique制約

同じプロフィール・同じ制度に対して状態レコードが重複しないようにする。

以下の組み合わせに unique 制約を付けること。

```text
profile_id + program_id
```

SQLAlchemyで可能なら `UniqueConstraint` を使用する。

## 5. API設計

## 5.1 GET /profile

保存済みプロフィールを取得する。

### レスポンス例

```json
{
  "id": 1,
  "name": "松岡拓志",
  "prefecture": "京都府",
  "city": "京都市",
  "ward": "左京区",
  "birthDate": "2003-04-01",
  "gender": "male",
  "householdIncome": "200万円〜400万円未満",
  "annualIncomeMax": 4000000,
  "monthlyIncome": 150000,
  "savingsAmountRange": "under_500k",
  "housingStatus": "rented",
  "familyType": "独身",
  "hasSpouse": false,
  "childrenCount": 0,
  "hasChildren": false,
  "isSingleParent": false,
  "isTaxExemptHousehold": null,
  "isHouseholdHead": null,
  "employment": {
    "employmentStatus": "student",
    "isUnemployed": false,
    "unemployedSince": null,
    "isJobSeeking": false,
    "incomeDecreased": false,
    "incomeDecreasedReason": null
  },
  "specialConditions": {
    "hasHealthInsurance": true,
    "isPregnant": false,
    "postpartumMonths": null,
    "hasDisability": false,
    "disabilityType": null,
    "disabilityGrade": null,
    "hasMedicalCareChild": false,
    "hasCareRequiredFamily": false,
    "hasYoungCarerInHousehold": false
  }
}
```

### プロフィール未登録時

```http
404 Not Found
```

```json
{
  "detail": "Profile not found"
}
```

## 5.2 PUT /profile

プロフィールを登録・更新する。

認証なしMVPのため、基本的に最新1件を更新する方針でよい。

既存実装が「id=1固定」や「最初の1件を更新」という方式なら、それに合わせる。

### リクエスト例

```json
{
  "name": "松岡拓志",
  "prefecture": "京都府",
  "city": "京都市",
  "ward": "左京区",
  "birthYear": "2003",
  "birthMonth": "4",
  "birthDay": "1",
  "householdIncome": "200万円〜400万円未満",
  "monthlyIncome": 150000,
  "savingsAmountRange": "under_500k",
  "housingStatus": "rented",
  "familyType": "独身",
  "childrenCount": "0",
  "gender": "男性",
  "taxExempt": "わからない",
  "isHouseholdHead": null,
  "employment": {
    "employmentStatus": "student",
    "isUnemployed": false,
    "unemployedSince": null,
    "isJobSeeking": false,
    "incomeDecreased": false,
    "incomeDecreasedReason": null
  },
  "specialConditions": {
    "hasHealthInsurance": true,
    "isPregnant": false,
    "postpartumMonths": null,
    "hasDisability": false,
    "disabilityType": null,
    "disabilityGrade": null,
    "hasMedicalCareChild": false,
    "hasCareRequiredFamily": false,
    "hasYoungCarerInHousehold": false
  }
}
```

### 注意

既存フロントが以下のような古い形式で送ってくる場合も受け取れるようにする。

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

つまり、追加項目はすべて optional とする。

## 5.3 GET /program-statuses

ユーザーが保存した制度状態一覧を取得する。

### レスポンス例

```json
[
  {
    "programId": 1,
    "status": "checking",
    "isFavorite": true,
    "memo": "区役所に確認する",
    "lastViewedAt": "2026-05-15T10:00:00",
    "updatedAt": "2026-05-15T10:00:00"
  }
]
```

### 備考

制度タイトルなどを含めるかどうかは任意である。

実装を簡単にするなら、まずは `programId` のみでよい。

時間があれば、`support_programs` とJOINして以下のようにしてもよい。

```json
{
  "programId": 1,
  "programTitle": "住居確保給付金",
  "status": "checking",
  "isFavorite": true,
  "memo": "区役所に確認する"
}
```

## 5.4 PUT /program-statuses/{program_id}

指定した制度に対するユーザー状態を作成・更新する。

今回のv2実装では、このAPI実行時に `last_viewed_at` を現在時刻で更新する。

### リクエスト例

```json
{
  "status": "checking",
  "isFavorite": true,
  "memo": "区役所に確認する"
}
```

### レスポンス例

```json
{
  "programId": 1,
  "status": "checking",
  "isFavorite": true,
  "memo": "区役所に確認する",
  "lastViewedAt": "2026-05-15T10:00:00",
  "updatedAt": "2026-05-15T10:00:00"
}
```

### 挙動

* プロフィールが存在しない場合は404
* program_id が存在しない場合は404
* 既存レコードがある場合は更新（および `last_viewed_at` 更新）
* 既存レコードがない場合は作成（および `last_viewed_at` 設定）

## 6. 入力変換ルール

## 6.1 birthYear / birthMonth / birthDay

既存通り、以下3項目から `birth_date` を作成する。

```text
birthYear
birthMonth
birthDay
```

DBには date 型として保存する。

## 6.2 gender

フロントから日本語で届いた場合は以下に変換する。

| 入力    | 保存値       |
| ----- | --------- |
| 男性    | male      |
| 女性    | female    |
| その他   | other     |
| 回答しない | no_answer |

すでに `male` 等で届いた場合は、そのまま受け取ってよい。

## 6.3 taxExempt

| 入力    | 保存値   |
| ----- | ----- |
| はい    | true  |
| いいえ   | false |
| わからない | null  |
| null  | null  |

DBカラムは `is_tax_exempt_household`。

## 6.4 childrenCount

文字列で届く可能性があるため、int に変換する。

未入力の場合は 0 とする。

`children_count > 0` の場合、`has_children = true` とする。

## 6.5 householdIncome

既存MVPの変換ルールを維持する。

例：

| 入力              | annual_income_max |
| --------------- | ----------------: |
| 200万円未満         |           2000000 |
| 200万円〜400万円未満   |           4000000 |
| 400万円〜600万円未満   |           6000000 |
| 600万円〜800万円未満   |           8000000 |
| 800万円〜1,000万円未満 |          10000000 |
| 1,000万円以上       |              null |

## 6.6 housingStatus

| 入力             | 保存値                 |
| -------------- | ------------------- |
| 持ち家           | owned               |
| 賃貸             | rented              |
| 公営住宅         | public_housing      |
| 家族と同居（実家等） | living_with_family  |
| その他           | other               |
| わからない       | unknown             |

## 7. Repository / Service の責務

### 7.1 repository

DBアクセスのみを担当する。

* profileの取得
* profileの作成・更新
* employment statusの作成・更新
* special conditionsの作成・更新
* user_program_statusの取得・作成・更新

### 7.2 service

入力変換や業務ロジックを担当する。

* birth date変換
* gender変換
* household income変換
* children count変換
* 既存profileがある場合は更新、ない場合は作成
* user_program_status の upsert

## 8. main.py へのrouter登録

`program_statuses.py` を作成したら、`app/main.py` にrouterを登録する。

例：

```python
from app.routers import program_statuses

app.include_router(program_statuses.router)
```

既存のimport形式に合わせること。

## 9. テスト・動作確認

最低限、以下を確認する。

### 9.1 プロフィール登録

```http
PUT /profile
```

* 旧形式のリクエストで登録できる
* 新形式のリクエストで登録できる
* `user_profiles` に保存される
* `profile_employment_statuses` に保存される
* `profile_special_conditions` に保存される

### 9.2 プロフィール取得

```http
GET /profile
```

* 拡張項目を含めて取得できる
* employment が取得できる
* specialConditions が取得できる

### 9.3 制度状態更新

```http
PUT /program-statuses/{program_id}
```

* program_id が存在する場合、状態を保存できる
* 2回目の実行では新規作成ではなく更新される
* status enum が正しく保存される

### 9.4 制度状態一覧

```http
GET /program-statuses
```

* 保存済みの状態一覧が取得できる

## 10. 担当Aの完了条件

担当Aの完了条件は以下である。

* `user_profiles` に city / ward / monthly_income / savings_amount_range / housing_status / is_household_head が追加されている
* `profile_employment_statuses` が作成されている
* `profile_special_conditions` が作成されている
* `user_program_statuses` が作成されている
* `PUT /profile` で旧形式・新形式の両方を受け取れる
* `GET /profile` で拡張プロフィールを取得できる
* `PUT /program-statuses/{program_id}` で制度状態を保存・更新できる
* `GET /program-statuses` で制度状態一覧を取得できる
* 既存の `GET /matches` が起動不能になっていない
