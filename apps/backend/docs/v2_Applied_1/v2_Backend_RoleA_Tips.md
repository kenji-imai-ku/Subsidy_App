# 担当A 実装ナレッジ・トラブルシューティング

このドキュメントは、v2バックエンド拡張（担当A）の実装過程で発生した技術的課題や、設計ドキュメントの指示だけでは不足していた点、およびその解決策をまとめたものである。

## 1. Pydantic v2 における Schema マッピングの注意点

最も大きな課題は、SQLAlchemy モデル（snake_case）から Pydantic Schema（camelCase）への変換におけるマッピング不全であった。

### 課題
設計ドキュメントでは `alias` を用いて camelCase に変換する指示があったが、Pydantic v2 において `from_attributes=True` で SQLAlchemy オブジェクトからデータを読み取る場合、`alias` だけでは不十分なケースがある。

特に、**「入力（バリデーション）」と「出力（シリアライズ）」の両方で異なる名前を扱う場合**、明示的な指定が必要となる。

### 解決策
Pydantic v2 の `validation_alias` と `serialization_alias` を併用し、さらに `ConfigDict` を使用する。

```python
from pydantic import BaseModel, Field, ConfigDict

class UserProgramStatusResponse(BaseModel):
    # validation_alias: DBモデル（snake_case）からの読み込み用
    # serialization_alias: APIレスポンス（camelCase）での出力用
    programId: int = Field(..., validation_alias="program_id", serialization_alias="programId")
    isFavorite: bool = Field(..., validation_alias="is_favorite", serialization_alias="isFavorite")

    # Pydantic v2 の新形式設定
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
```

## 2. 1対1リレーションの Upsert 実装

`UserProfile` と `ProfileEmploymentStatus` などの1対1リレーションにおいて、親レコードの更新時に子レコードをどう扱うかが実装上のポイントとなった。

### 課題
`update_profile` 時に、関連する子テーブルのレコードが存在しない場合に `AttributeError` になる、あるいは古いデータを上書きできないリスクがあった。

### 解決策
Repository層で、関連オブジェクトの存在確認を行い、分岐処理を明示的に書く。

```python
def update_profile(db: Session, profile: UserProfile, data: dict) -> UserProfile:
    employment_data = data.pop("employment", None)
    # ... 本体更新 ...
    if employment_data:
        if profile.employment:
            # 存在すれば値を更新
            for key, value in employment_data.items():
                setattr(profile.employment, key, value)
        else:
            # 存在しなければ新規作成
            profile.employment = ProfileEmploymentStatus(**employment_data)
```

## 3. 入力値の柔軟な変換

既存フロントエンドとの互換性を保つため、`taxExempt` などの boolean 項目が「日本語（はい/いいえ）」「真偽値（true/false）」「文字列の "true"/"false"」のいずれで届いても壊れないようにする必要があった。

### 解決策
Service層の `convert_profile_request` において、`dict.get()` によるマッピングだけでなく、文字列判定を組み合わせた。

```python
tax_exempt_val = TAX_EXEMPT_MAP.get(request.taxExempt, None)
if request.taxExempt not in TAX_EXEMPT_MAP:
     if str(request.taxExempt).lower() == "true":
         tax_exempt_val = True
     elif str(request.taxExempt).lower() == "false":
         tax_exempt_val = False
```

## 4. 既存 `matching_service.py` への配慮

DBモデルを拡張した際、既存の `matching_service.py` が `UserProfile` オブジェクトを直接操作している場合、スキーマの変更が予期せぬエラー（None参照など）を引き効き起こす可能性がある。

### 対策
- 新規追加カラムはすべて `nullable=True` (Optional) とし、デフォルト値（`default=0` など）を適切に設定する。
- リレーション追加時は `cascade="all, delete-orphan"` を設定し、親の削除時にゴミが残らないようにする。
