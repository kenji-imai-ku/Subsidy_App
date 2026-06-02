# マッチング精度向上のための「特殊条件フラグ」実装計画

## 背景と目的
現在、火災などの被災者向けといった「極めて限定的・突発的な状況」を対象とした制度が、一般的なユーザーに対してもマッチ度100点として表示されてしまう課題がある。
これを解決するため、AI抽出時にそのような特殊な制度であるかを判定し、データベースにフラグとして保持させ、マッチングロジックにおいてスコアを調整する仕組みを導入する。

## 実装方針（案1：スキーマ拡張による対応）
データベースの `support_program_conditions` テーブルに `is_extraordinary_condition` という Boolean カラムを追加し、AI抽出からマッチング計算までを一気通貫で連携させる。

## 変更対象ファイルと具体的な修正内容

### 1. データベースモデルの修正
**対象ファイル:** `apps/backend/app/models/support_program.py`
*   `SupportProgramCondition` クラスに以下を追加する。
    ```python
    is_extraordinary_condition = Column(Boolean, nullable=False, default=False)
    ```

### 2. Pydanticスキーマの修正
**対象ファイル:** `apps/backend/app/schemas/support_program.py`
*   `ProgramConditionCreateRequest` クラスに以下を追加する。
    ```python
    isExtraordinaryCondition: Optional[bool] = Field(default=False, validation_alias=AliasChoices("is_extraordinary_condition", "isExtraordinaryCondition"))
    ```
*   `ProgramConditionResponse` クラスに以下を追加する。
    ```python
    isExtraordinaryCondition: Optional[bool] = Field(default=False, validation_alias=AliasChoices("is_extraordinary_condition", "isExtraordinaryCondition"))
    ```

### 3. スクリプト (AI抽出ロジック) の修正
**対象ファイル:** `apps/backend/scripts/import_programs_from_markdown.py`
*   `ProgramConditionCandidate` クラスに以下を追加する。
    ```python
    is_extraordinary_condition: bool = Field(False, description="火災、天災、犯罪被害など、極めて稀で突発的な状況を対象とした制度か")
    ```
*   `SYSTEM_PROMPT` のルールに以下の指示を追加する。
    ```text
    13. 火災による被災、天災、犯罪被害など、全人口において該当する確率が極めて低い「突発的・限定的な特殊状況」を対象とした制度の場合は、condition内の is_extraordinary_condition を true にしてください。
    ```
*   必要に応じて DB 登録リクエスト生成部 (`condition_dict` のマッピング等) で、正しく `isExtraordinaryCondition` として渡ることを確認する（自動の camelCase 変換が適用されるため、基本的には変更不要の見込み）。

### 4. マッチングロジックの修正
**対象ファイル:** `apps/backend/app/services/matching_service.py`
*   `calculate_match_score` 関数内に、以下の減点ロジックを追加する。
    ```python
    # 6. 特殊条件・人間確認 (v2拡張) のセクション付近に追加
    if condition and getattr(condition, "is_extraordinary_condition", False) is True:
        score -= 30  # 特殊条件の場合は基本スコアを下げる（例：70点スタートにする）
        warnings.append("災害や特殊な被害等に遭われた方向けの限定的な制度です")
    ```

## 懸念事項と対策
*   **既存データへの影響**: データベーススキーマを変更するため、既存の `app.db` をそのまま使用するとカラムが存在せずエラーになる。
    *   **対策**: `apps/backend/update_models_and_schemas.sh` などの移行手段がない場合、一度 `app.db` を削除し、再度 `run_full_pipeline.py` を実行してデータを再構築する必要がある。
*   **APIとDBの命名規則**: `import_programs_from_markdown.py` 側で camelCase への変換が行われるため、スキーマで `isExtraordinaryCondition` を定義しておけば、DB層へのマッピングは `program_service.py` で `is_extraordinary_condition` に正しく変換される。

## 実施手順
1. 上記4つのファイルを計画通りに修正する。
2. データベース (`app.db`) をリセット（削除）する。
3. `poetry run python scripts/run_full_pipeline.py --limit 10` などを実行し、エラーなく抽出およびDB登録が完了するかテストする。
4. フロントエンド（またはAPI）でマッチング結果を確認し、特殊な制度のスコアが下がっているか検証する。
5. 実装完了後、この計画書を `apps/backend/docs/v3_Applied_2_latest/02_Matching_Refinement_Design.md` にコピーする。
