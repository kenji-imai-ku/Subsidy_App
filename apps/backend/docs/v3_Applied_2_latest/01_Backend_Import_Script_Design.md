# Markdownからの支援制度取り込みバッチ 設計ドキュメント

## 背景と目的
支援制度ページのMarkdownファイルを入力として、LLMを用いて情報を抽出し、既存のDBスキーマに登録するCLIバッチを実装する。LLMの出力に対する検証(Pydantic)や正規化を導入し、不正なデータがDBに混入することを防ぐ。

## 今回の対象範囲
- `apps/backend/output/*.md` を読み込む処理
- LLM (OpenAI API) による情報抽出
- 抽出結果の正規化 (日本語表現等の表記ゆれをEnumの英語値に寄せる)
- Pydantic による構造・Enum検証
- 検証エラー時のLLMへの再試行 (最大2回)
- 抽出・検証完了したデータの既存DB (`support_programs`, `support_program_conditions`, `program_sources`) への登録
- CLIとしての実行機能 (`--dry-run` 対応、特定ファイルの指定 `--file`)

## アーキテクチャと設計方針
1. **Pydantic Enumの活用**: `support_type`, `benefit_amount_type`, `application_method` などの重要項目にはPydantic Enumを定義して検証する。
2. **中間スキーマ**: DBモデルに直接マッピングせず、LLM抽出用の「Candidateスキーマ」をPydanticで定義し、検証後 DB向けデータに変換する。
3. **正規化の徹底**: Pydanticの `BeforeValidator` などを利用して、LLM出力の揺れ（「補助金」→「subsidy」など）を正規化してからEnum検証を通す。
4. **既存処理の再利用**: DB登録は `app.services.program_service.create_program` に依存するPydanticのRequestモデル（`ProgramCreateRequest`）等を利用し、既存ルートを活用する。
5. **DB制約は防衛線**: 主な制約はPydanticで担保し、DBエラー時はスキップする設計。

## 実装構成
- **スクリプト**: `apps/backend/scripts/import_programs_from_markdown.py` (CLIのエントリポイント)
- **スキーマ**: スクリプト内または `app/schemas` 下にLLM制約用の `MarkdownProgramExtractionSchema` 等を追加。
- **Enum定義**: `app/schemas` やスクリプト内に `SupportType`, `BenefitAmountType` 等のEnumとマッピング辞書を追加。

## 実装計画

### 1. 現在の設計理解
- 既存のDB設計では `support_programs` と `support_program_conditions`、`program_sources`、`program_required_documents` テーブルが存在します。
- SQLAlchemyによるモデルと、FastAPI向け等に作られたPydanticスキーマ (`ProgramCreateRequest`, `ProgramConditionCreateRequest` など) が存在します。
- DB登録処理は `program_service.create_program` に存在し、PydanticのRequestモデルを受け取って `program_repository.create_program` を呼び出す形で整理されています。
- 現在 `support_type` や `benefit_amount_type` などには厳格なDB制約（Enum/CHECK）はなくString型のようですが、アプリケーション層である程度バリデーションが可能な設計になっています。

### 2. 追加・変更するファイル一覧
- **追加**: `apps/backend/scripts/import_programs_from_markdown.py` (バッチ本体、抽出・正規化・検証ロジックをここに集約)
- (既存のファイルはできるだけ変更せず、新規スクリプト内で閉じ込めることを基本としますが、必要に応じて `pyproject.toml` に `openai` 等を追加します)

### 3. 追加する Pydantic schema
LLM抽出の中間受け皿として、以下の `Candidate Schema` をスクリプト内に定義します。
- `ProgramConditionCandidate`
- `ProgramSourceCandidate`
- `ProgramExtractionCandidate`
これらはLLMに出力させるJSONの構造を厳密に定義し、フィールドには `BeforeValidator` による正規化を仕込みます。

### 4. 追加する Enum
以下のEnumクラスを定義し、Pydanticスキーマの型として指定します。
- `SupportType` (cash, subsidy, medical, etc.)
- `BenefitAmountType` (fixed, max_amount, depends, free_text, unknown)
- `BenefitUnit` (per_person, per_child, etc.)
- `ApplicationMethod` (online, mail, counter, etc.)
- `ApplicationPeriodType` (always, deadline, limited, unknown)
- `ConfidenceLevel` (official, manual_checked, estimated, dummy)

### 5. 追加する正規化処理
各Enumに対して、入力文字列（日本語表現のゆらぎ）を内部の英語値に変換する `alias mapping` (辞書) を定義します。
Pydanticの `field_validator(..., mode="before")` (または `BeforeValidator`) を利用し、LLMが出力した自由入力の日本語（例：「オンライン申請」「現金給付」）をバリデーション前に正規化（マッピング）します。

### 6. 追加する LLM 抽出処理
`openai` パッケージを利用した関数を実装します。
`response_format` でJSONを出力するようにし（Structured Outputs を推奨）、プロンプトには要件に記載されたルール（ Enum値の指定、抽出根拠、推測の禁止など ）を明記します。

### 7. 追加する LLM 修正リトライ処理
`ProgramExtractionCandidate.model_validate_json()` で `ValidationError` が発生した場合に、キャッチして例外の文字列 (`str(e)`) と期待されるEnum値をプロンプトに含めて、再度LLMに「エラーを修正したJSONを出力して」と依頼するリトライループを最大2回回します。

### 8. 追加する CLI script の責務
- `argparse` による引数解析 (`--dry-run`, `--file`)
- `apps/backend/output/` 以下の `.md` ファイルを安全に取得・巡回
- 各ファイルに対し LLM抽出 → 正規化＆検証 → 既存DB形式へのマッピング を実行
- 抽出結果や進行状況の標準出力への表示
- トータル件数・成功・失敗・スキップ数のサマリー表示

### 9. 既存DB登録処理との接続方法
検証済みの `ProgramExtractionCandidate` を、既存の `ProgramCreateRequest` (および `ProgramConditionCreateRequest`, `ProgramSourceCreateRequest`) のインスタンスに変換し、 `app.core.database.SessionLocal` から得たDBセッションと共に `program_service.create_program` に渡してDB登録を行います。
重複登録を防ぐため、事前に `db.query(SupportProgram).filter_by(title=..., provider=...).first()` などで簡易チェックを入れます。

### 10. 既存設計と不整合が出そうな点
- 既存の `ProgramCreateRequest` はキャメルケース (`supportType` など) を受け取る設計になっており、 `model_dump` 時等にキーの不整合が起きないか注意が必要です。LLMからはスネークケースで出力させ、既存スキーマへ渡す際に適切にマッピングします。
- 既存の条件テーブル (`support_program_conditions`) にない項目は、`condition_description` にマージします。

## 実装結果と補足事項

### 1. 実装済み機能
- `apps/backend/scripts/import_programs_from_markdown.py` の実装完了。
- OpenAI Structured Outputs (`beta.chat.completions.parse`) を使用した高精度な情報抽出。
- Pydantic Enum と `BeforeValidator` による日本語表現の自動正規化。
- DB登録時の重複チェック（タイトルと実施主体の組み合わせ）。
- `--dry-run` および `--file` オプションのサポート。

### 2. 既存設計の修正内容
- `app/services/program_service.py` を修正しました。
  - Pydanticモデルから `model_dump()` した際のキャメルケースのキーを、SQLAlchemyモデルが期待するスネークケースに自動変換するロジックを追加しました。これにより、API経由およびスクリプト経由での登録が安定しました。

### 3. 実行方法
```bash
# apps/backend ディレクトリで実行
poetry run python scripts/import_programs_from_markdown.py --dry-run
poetry run python scripts/import_programs_from_markdown.py --file output/example.md
```

### 4. 依存関係の追加
- `openai` パッケージを追加しました。
- `app/core/config.py` に `openai_api_key` と `openai_model` を追加しました。

### 5. 今後の課題
- 重複チェックの強化（URL等を用いたより厳密な判定）。
- 抽出結果の人間による最終確認フローの構築（承認ステータスの導入）。
- 処理済みファイルの履歴管理機能。

