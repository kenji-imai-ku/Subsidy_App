# 03_Backend_RoleB_Program_Data_Implementation.md

# 担当B 実装指示書：支援制度データ・制度管理

## 1. 担当Bの目的

担当Bは、支援制度そのものと制度条件を拡張する。

今回の目的は、現金給付だけでなく、医療費助成、サービス利用料軽減、ヘルパー派遣、貸付、物品給付、相談支援など、実際の支援制度に近い多様な制度を表現できるDB構造とAPIを整備することである。

また、後続のマッチングロジックが利用できるように、制度条件をできる限り構造化して保存できるようにする。

## 2. 担当Bの実装範囲

担当Bは以下を実装する。

```text
DB / Model
- support_programs の拡張
- support_program_conditions の拡張
- program_sources の追加
- program_required_documents の追加、ただし後回し可

Schema
- support_program.py の拡張
- program_source.py の追加
- program_required_document.py の追加、ただし後回し可

Repository
- program_repository.py の拡張
- program_source_repository.py の追加、または program_repository に統合

Service
- program_service.py の拡張
- program_seed_service.py の追加、または seed_programs.py に統合

Router
- programs.py の拡張
- dev_programs.py の追加

Seed
- seed_programs.py の拡張

API
- GET /programs
- GET /programs/{program_id}
- POST /dev/seed/programs
- POST /dev/programs
- PUT /dev/programs/{program_id}
```

## 3. 担当Bが触る主なファイル

```text
app/models/support_program.py
app/models/program_source.py
app/models/program_required_document.py

app/schemas/support_program.py
app/schemas/program_source.py
app/schemas/program_required_document.py

app/repositories/program_repository.py
app/repositories/program_source_repository.py

app/services/program_service.py
app/services/program_seed_service.py

app/routers/programs.py
app/routers/dev_programs.py

app/seed/seed_programs.py

app/main.py  ※router追加時のみ最小限編集
```

`app/main.py` は担当Aも触る可能性があるため、編集はrouter登録など最小限にする。

## 4. DB設計

## 4.1 support_programs の拡張

既存の `support_programs` を拡張する。

既存カラムは可能な限り維持する。

追加後の想定カラムは以下である。

```text
id
title
provider
summary
benefit
category
support_type
benefit_amount_type
benefit_amount
benefit_unit
target_prefecture
target_city
target_ward
application_required
application_method
application_period_type
application_url
deadline
start_date
end_date
required_documents
contact_department
contact_phone
source_url
source_updated_at
data_confirmed_at
confidence_level
notes
is_active
created_at
updated_at
```

### 4.1.1 追加カラム

| カラム                     | 型              | 必須 | 説明            |
| ----------------------- | -------------- | -: | ------------- |
| support_type            | varchar / null | no | 支援の種類         |
| benefit_amount_type     | varchar / null | no | 金額の表現方法       |
| benefit_amount          | integer / null | no | 固定金額または上限金額   |
| benefit_unit            | varchar / null | no | 1人あたり、1世帯あたり等 |
| application_required    | boolean / null | no | 申請が必要か        |
| application_method      | varchar / null | no | 申請方法          |
| application_period_type | varchar / null | no | 申請期間の種類       |
| start_date              | date / null    | no | 制度開始日         |
| end_date                | date / null    | no | 制度終了日         |
| contact_department      | varchar / null | no | 担当部署          |
| contact_phone           | varchar / null | no | 問い合わせ先        |
| source_updated_at       | date / null    | no | 情報源の更新日       |
| data_confirmed_at       | date / null    | no | アプリ側で確認した日    |
| confidence_level        | varchar / null | no | データ信頼度        |
| notes                   | text / null    | no | 補足            |

### 4.1.2 support_type の値

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

### 4.1.3 benefit_amount_type の値

```text
fixed
max_amount
depends
free_text
unknown
```

### 4.1.4 benefit_unit の値

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

### 4.1.5 application_method の値

```text
online
mail
counter
automatic
not_required
unknown
```

### 4.1.6 application_period_type の値

```text
always
deadline
limited
unknown
```

### 4.1.7 confidence_level の値

```text
official
manual_checked
estimated
dummy
```

seedデータで仮データを作成する場合は `dummy` を使用する。

公式ページを参照して手入力した場合は `manual_checked` を使用する。

## 4.2 support_program_conditions の拡張

既存の `support_program_conditions` を拡張する。

既存カラムは可能な限り維持する。

追加後の想定カラムは以下である。

```text
id
program_id
min_age
max_age
max_annual_income
max_monthly_income
max_savings_amount
requires_tax_exempt
requires_children
min_children_count
requires_single_parent
required_gender
required_city
required_ward
requires_unemployed
unemployed_within_months
requires_job_seeking
requires_income_decreased
requires_health_insurance
requires_pregnancy
max_postpartum_months
requires_disability
required_disability_type
requires_medical_care_child
requires_young_carer
requires_household_head
requires_rent
condition_description
condition_text_original
manual_check_required
created_at
updated_at
```

### 4.2.1 追加カラム

| カラム                         | 型              |  必須 | 説明             |
| --------------------------- | -------------- | --: | -------------- |
| max_monthly_income          | integer / null |  no | 月収上限           |
| max_savings_amount          | integer / null |  no | 預貯金上限          |
| required_city               | varchar / null |  no | 対象市区町村         |
| required_ward               | varchar / null |  no | 対象区            |
| requires_unemployed         | boolean / null |  no | 離職中が必要か        |
| unemployed_within_months    | integer / null |  no | 離職後何か月以内か      |
| requires_job_seeking        | boolean / null |  no | 求職活動が必要か       |
| requires_income_decreased   | boolean / null |  no | 収入減少が必要か       |
| requires_health_insurance   | boolean / null |  no | 健康保険加入が必要か     |
| requires_pregnancy          | boolean / null |  no | 妊娠中が必要か        |
| max_postpartum_months       | integer / null |  no | 産後何か月以内か       |
| requires_disability         | boolean / null |  no | 障害要件           |
| required_disability_type    | varchar / null |  no | 障害種別           |
| requires_medical_care_child | boolean / null |  no | 医療的ケア児が必要か     |
| requires_young_carer        | boolean / null |  no | ヤングケアラー家庭か     |
| requires_household_head     | boolean / null |  no | 世帯主が必要か        |
| requires_rent               | boolean / null |  no | 賃貸住宅が必要か       |
| condition_text_original     | text / null    |  no | 元ページの条件文       |
| manual_check_required       | boolean        | yes | 人間確認が必要な条件を含むか |

### 4.2.2 manual_check_required

`manual_check_required` は必ず用意する。

制度条件には、機械判定しにくいものが存在するためである。

例：

```text
市長が必要と認める家庭
生活に困窮していると認められる場合
その他、自治体が必要と認める場合
```

このような条件を完全に自動判定することは難しい。

そのため、該当する制度条件では以下のように保存する。

```text
manual_check_required = true
condition_text_original = 元の条件文
condition_description = 人間向けの簡潔な説明
```

後続のマッチングロジックでは、これを warnings に出す想定である。

## 4.3 program_sources テーブル

制度情報の情報源を保存する。

```text
program_sources
```

| カラム              | 型               |  必須 | 説明                          |
| ---------------- | --------------- | --: | --------------------------- |
| id               | integer         | yes | ID                          |
| program_id       | integer         | yes | support_programs.id への外部キー  |
| source_url       | text            | yes | 情報源URL                      |
| source_type      | varchar         | yes | html / pdf / manual / other |
| title            | varchar / null  |  no | ページタイトル                     |
| publisher        | varchar / null  |  no | 掲載元                         |
| published_at     | date / null     |  no | 公開日                         |
| last_modified_at | date / null     |  no | ページ更新日                      |
| fetched_at       | datetime / null |  no | Web取得日。今回は基本nullでよい         |
| checked_at       | datetime / null |  no | 人間が確認した日                    |
| raw_text         | text / null     |  no | 抽出テキスト。今回はnull可             |
| notes            | text / null     |  no | 補足                          |
| created_at       | datetime        | yes | 作成日時                        |
| updated_at       | datetime / null |  no | 更新日時                        |

### 4.3.1 source_type の値

```text
html
pdf
manual
other
```

### 4.3.2 関係

`support_programs` と `program_sources` は 1対多 とする。

```text
SupportProgram 1 -- N ProgramSource
```

1つの制度に複数の情報源が紐づく可能性があるためである。

## 4.4 program_required_documents テーブル

必要書類を構造化して保存する。

このテーブルは時間がなければ後回しでよい。

ただし、実装する場合は以下とする。

```text
program_required_documents
```

| カラム           | 型               |  必須 | 説明                         |
| ------------- | --------------- | --: | -------------------------- |
| id            | integer         | yes | ID                         |
| program_id    | integer         | yes | support_programs.id への外部キー |
| document_name | varchar         | yes | 書類名                        |
| is_required   | boolean         | yes | 必須か                        |
| notes         | text / null     |  no | 補足                         |
| created_at    | datetime        | yes | 作成日時                       |
| updated_at    | datetime / null |  no | 更新日時                       |

## 5. API設計

## 5.1 GET /programs

制度一覧を取得する。

既存APIを維持しつつ、クエリパラメータを拡張する。

### 対応するクエリパラメータ

| パラメータ               | 型       | 例         | 説明      |
| ------------------- | ------- | --------- | ------- |
| category            | string  | childcare | カテゴリ    |
| supportType         | string  | cash      | 支援タイプ   |
| prefecture          | string  | 京都府       | 対象都道府県  |
| city                | string  | 京都市       | 対象市区町村  |
| ward                | string  | 左京区       | 対象区     |
| applicationRequired | boolean | true      | 申請が必要か  |
| activeOnly          | boolean | true      | 有効な制度のみ |
| keyword             | string  | 医療費       | キーワード検索 |

### リクエスト例

```http
GET /programs?category=childcare&supportType=medical&prefecture=京都府&city=京都市&activeOnly=true
```

### レスポンス例

```json
[
  {
    "id": 1,
    "title": "子ども医療費支給制度",
    "provider": "京都市",
    "summary": "子どもの医療費の自己負担を軽減する制度です。",
    "benefit": "医療費の一部を助成",
    "category": "childcare",
    "supportType": "medical",
    "benefitAmountType": "depends",
    "benefitAmount": null,
    "benefitUnit": "per_child",
    "targetPrefecture": "京都府",
    "targetCity": "京都市",
    "targetWard": null,
    "applicationRequired": true,
    "applicationMethod": "counter",
    "applicationUrl": "https://example.com",
    "deadline": null,
    "confidenceLevel": "dummy",
    "isActive": true
  }
]
```

## 5.2 GET /programs/{program_id}

制度詳細を取得する。

### レスポンス例

```json
{
  "id": 1,
  "title": "子ども医療費支給制度",
  "provider": "京都市",
  "summary": "子どもの医療費の自己負担を軽減する制度です。",
  "benefit": "医療費の一部を助成",
  "category": "childcare",
  "supportType": "medical",
  "benefitAmountType": "depends",
  "benefitAmount": null,
  "benefitUnit": "per_child",
  "targetPrefecture": "京都府",
  "targetCity": "京都市",
  "targetWard": null,
  "applicationRequired": true,
  "applicationMethod": "counter",
  "applicationPeriodType": "always",
  "applicationUrl": "https://example.com",
  "deadline": null,
  "startDate": null,
  "endDate": null,
  "requiredDocuments": "健康保険証、本人確認書類など",
  "contactDepartment": "子ども若者はぐくみ局",
  "contactPhone": null,
  "sourceUrl": "https://example.com/source",
  "sourceUpdatedAt": null,
  "dataConfirmedAt": null,
  "confidenceLevel": "dummy",
  "notes": null,
  "isActive": true,
  "condition": {
    "minAge": null,
    "maxAge": 15,
    "maxAnnualIncome": null,
    "maxMonthlyIncome": null,
    "requiresChildren": true,
    "minChildrenCount": 1,
    "requiresHealthInsurance": true,
    "conditionDescription": "京都市在住で健康保険に加入している中学校3年生までの子どもが対象です。",
    "conditionTextOriginal": null,
    "manualCheckRequired": false
  },
  "sources": [
    {
      "sourceUrl": "https://example.com/source",
      "sourceType": "html",
      "title": "子ども医療費支給制度",
      "publisher": "京都市",
      "checkedAt": null
    }
  ],
  "requiredDocumentItems": []
}
```

`requiredDocumentItems` は `program_required_documents` を実装しない場合、空配列でよい。

## 5.3 POST /dev/seed/programs

開発用seedデータを投入する。

### 挙動

以下のいずれかの方式でよい。

#### 方式A：既存データを残して不足分だけ追加

既存の制度タイトルとproviderの組み合わせを見て、重複しないものだけ追加する。

#### 方式B：既存seedデータを削除して再投入

開発環境であれば、既存seedデータを削除して再投入してもよい。

ただし、削除対象はseedで作成した制度のみにするのが望ましい。

### レスポンス例

```json
{
  "inserted": 10,
  "message": "Seed programs inserted successfully"
}
```

## 5.4 POST /dev/programs

開発用に制度を手動作成するAPI。

### リクエスト例

```json
{
  "title": "仮の子育て応援給付金",
  "provider": "京都市",
  "summary": "子育て世帯を支援するための仮制度です。",
  "benefit": "対象児童1人あたり1万円を支給します。",
  "category": "childcare",
  "supportType": "cash",
  "benefitAmountType": "fixed",
  "benefitAmount": 10000,
  "benefitUnit": "per_child",
  "targetPrefecture": "京都府",
  "targetCity": "京都市",
  "targetWard": null,
  "applicationRequired": true,
  "applicationMethod": "online",
  "applicationPeriodType": "deadline",
  "applicationUrl": "https://example.com/apply",
  "deadline": "2026-12-31",
  "confidenceLevel": "dummy",
  "condition": {
    "maxAge": 18,
    "requiresChildren": true,
    "minChildrenCount": 1,
    "conditionDescription": "18歳以下の子どもがいる世帯が対象です。",
    "manualCheckRequired": false
  },
  "sources": [
    {
      "sourceUrl": "https://example.com/source",
      "sourceType": "manual",
      "title": "仮データ",
      "publisher": "開発用"
    }
  ]
}
```

### レスポンス

作成した制度詳細を返す。

## 5.5 PUT /dev/programs/{program_id}

開発用に制度を更新するAPI。

### 挙動

* program_id が存在しない場合は404
* 指定された項目のみ更新してもよい
* 実装を簡単にするなら、全項目更新でもよい
* condition / sources も更新できると望ましいが、時間がなければ program本体のみでもよい

## 6. GET /programs の絞り込み仕様

## 6.1 activeOnly

`activeOnly=true` の場合は `is_active = true` の制度のみ返す。

未指定の場合は、既存実装に合わせる。

方針がなければ `activeOnly=true` をデフォルトとする。

## 6.2 category

`support_programs.category` と完全一致でよい。

## 6.3 supportType

`support_programs.support_type` と完全一致でよい。

## 6.4 prefecture / city / ward

以下のように扱う。

* `target_prefecture` が null の制度は全国制度または地域未指定として扱い、除外しない
* `target_prefecture` が指定されている制度は、クエリの prefecture と一致する場合のみ返す
* city / ward も同様に扱う

実装を簡単にする場合、まずは完全一致でよい。

## 6.5 applicationRequired

`application_required` と一致する制度を返す。

## 6.6 keyword

まずは以下のカラムに対する部分一致でよい。

```text
title
summary
benefit
provider
```

SQLiteの場合、大文字小文字や日本語検索の厳密性は気にしなくてよい。

## 7. seedデータ設計

今回のseedでは、制度タイプの幅を広げることを重視する。

最低10件程度の制度を作成する。

実在制度を参考にしてよいが、正確性に自信がない場合は `confidence_level = dummy` とし、仮データとして扱う。

## 7.1 seedに含める制度例

| No | 制度名            | support_type     | category   | 条件の練習になる項目      |
| -: | -------------- | ---------------- | ---------- | --------------- |
|  1 | 住居確保給付金        | subsidy          | housing    | 離職、収入減少、求職、家賃   |
|  2 | 子ども医療費支給制度     | medical          | childcare  | 子ども、年齢、健康保険、居住地 |
|  3 | ひとり親家庭等医療費支給制度 | medical          | childcare  | ひとり親、子ども、所得     |
|  4 | 育児支援ヘルパー派遣事業   | service_dispatch | childcare  | 産後、非課税世帯、育児支援   |
|  5 | 産後ケア事業         | service_discount | childcare  | 産後、母子、所得        |
|  6 | 日常生活用具の給付      | goods            | disability | 障害、難病、所得        |
|  7 | 生活福祉資金貸付制度     | loan             | livelihood | 低所得、障害、高齢、貸付    |
|  8 | 低所得世帯向け給付金     | cash             | livelihood | 非課税世帯、自動支給      |
|  9 | 子育て応援手当        | cash             | childcare  | 子ども、申請要否        |
| 10 | 就学援助制度         | subsidy          | education  | 小中学生、所得、自治体     |

## 7.2 seedデータ作成時の注意

* 仮データの場合、`confidence_level = dummy` にする
* `source_url` は仮URLでもよいが、空欄でもよい
* `support_type` は必ず設定する
* `application_required` は可能な限り設定する
* `application_method` は不明なら `unknown`
* `manual_check_required` は、機械判定しにくい条件がある場合 true
* `condition_description` はユーザーが読める自然な日本語にする

## 8. Repository / Service の責務

### 8.1 repository

DBアクセスのみを担当する。

* 制度一覧取得
* 制度詳細取得
* 制度作成
* 制度更新
* 条件作成・更新
* 情報源作成・取得
* seed投入用の登録処理

### 8.2 service

業務ロジックを担当する。

* クエリパラメータに応じた検索条件の組み立て
* program / condition / source をまとめたレスポンス作成
* seedデータ作成
* dev API の入力整形

## 9. main.py へのrouter登録

`dev_programs.py` を作成したら、`app/main.py` にrouterを登録する。

例：

```python
from app.routers import dev_programs

app.include_router(dev_programs.router)
```

既存のimport形式に合わせること。

## 10. テスト・動作確認

最低限、以下を確認する。

### 10.1 seed投入

```http
POST /dev/seed/programs
```

* 10件程度の制度が作成される
* `support_programs` に保存される
* `support_program_conditions` に保存される
* `program_sources` に保存される

### 10.2 制度一覧

```http
GET /programs
```

* 制度一覧が取得できる
* supportTypeで絞り込める
* categoryで絞り込める
* prefecture / cityで絞り込める
* keywordで検索できる

### 10.3 制度詳細

```http
GET /programs/{program_id}
```

* 拡張項目が取得できる
* conditionが取得できる
* sourcesが取得できる

### 10.4 dev作成API

```http
POST /dev/programs
```

* 制度を作成できる
* conditionも保存できる
* sourcesも保存できる

### 10.5 dev更新API

```http
PUT /dev/programs/{program_id}
```

* 制度を更新できる
* 存在しないIDでは404になる

## 11. 担当Bの完了条件

担当Bの完了条件は以下である。

* `support_programs` に support_type / application_required / application_method / benefit_amount_type 等が追加されている
* `support_program_conditions` に就労・収入減少・妊娠出産・障害・健康保険などの条件カラムが追加されている
* `program_sources` が作成されている
* `GET /programs` で拡張項目を含む一覧を取得できる
* `GET /programs/{program_id}` で condition / sources を含む詳細を取得できる
* `GET /programs` で category / supportType / prefecture / city / keyword などの絞り込みができる
* `POST /dev/seed/programs` で複数タイプのseedデータを投入できる
* `POST /dev/programs` で制度を作成できる
* `PUT /dev/programs/{program_id}` で制度を更新できる
* 既存の `GET /matches` が起動不能になっていない

## 12. 後続マッチング実装者への引き継ぎ

担当Bは、制度条件のうち、機械的に判定できるものと、人間確認が必要なものを分けて保存すること。

特に以下のカラムは後続マッチング実装で重要になる。

```text
support_program_conditions.min_age
support_program_conditions.max_age
support_program_conditions.max_annual_income
support_program_conditions.max_monthly_income
support_program_conditions.max_savings_amount
support_program_conditions.requires_tax_exempt
support_program_conditions.requires_children
support_program_conditions.requires_single_parent
support_program_conditions.requires_unemployed
support_program_conditions.requires_job_seeking
support_program_conditions.requires_income_decreased
support_program_conditions.requires_health_insurance
support_program_conditions.requires_pregnancy
support_program_conditions.max_postpartum_months
support_program_conditions.requires_disability
support_program_conditions.required_disability_type
support_program_conditions.manual_check_required
support_program_conditions.condition_text_original
```

後続のマッチングロジックでは、これらを参照して以下を返す想定である。

```text
- eligible
- possible
- not_applicable
- reasons
- warnings
- missing_information
```

今回の担当B実装では、そこまでの判定ロジックは作り込まなくてよい。

制度条件を正しく保存・取得できる状態にすることを優先する。
