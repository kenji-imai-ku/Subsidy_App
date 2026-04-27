# 🚀 Team4 App モノリポ開発ガイド

このプロジェクトは、**Next.js (フロントエンド)** と **FastAPI (バックエンド)** を組み合わせたモノリポ構成です。

Dockerを使わずに、チーム全体の開発環境（ランタイム・ライブラリ）を完全に一致させる仕組みを採用しています。

以下簡単にセットアップの方法を記載しています。

不明点ありましたら、AIと解決を試み、解決できない場合は平松にお気軽にご相談ください！
---

## 🛠 1. 事前準備 (初回のみ)

開発を始める前に、以下の3つのツールを必ずインストールしてください。

### ① mise (ランタイム管理)
Node.js と Python のバージョンをプロジェクトごとに自動で切り替えます。
- **Mac:** `brew install mise`
- **Linux/WSL2:** `curl https://mise.jdx.dev/install.sh | sh`
- [インストールガイド](https://mise.jdx.dev/getting-started.html)

### ② Poetry (Pythonパッケージ管理)
バックエンドの依存関係を厳密に管理します。
- **Mac/Linux/WSL2:** `curl -sSL https://install.python-poetry.org | python3 -`
- ※インストール後、パスを通す設定（`export PATH="$HOME/.local/bin:$PATH"`）が必要な場合があります。

### ③ pnpm (Nodeパッケージ管理)
高速なパッケージマネージャーです。
- **共通:** `npm install -g pnpm`

---

## 📥 2. セットアップ手順

リポジトリをクローンした後、**プロジェクトのルートディレクトリ**で以下のコマンドを実行してください。

```bash
# 1. 適切な Node.js と Python を自動インストール
mise install

# 2. フロントとバックの依存関係を一括インストール
pnpm install:all
```

## 💻 3. 開発コマンド

### 全サービスの一括起動 (Turborepo)
```bash
pnpm dev
```
- Frontend: http://localhost:3000
- Backend: http://localhost:8000

フロントとバックのログが統合されてターミナルに表示されます。

### 個別起動
- フロントのみ: `pnpm --filter frontend dev`
- バックのみ: `pnpm --filter backend dev`


## ⚠️ 4. 開発上のルール (重要)
### ライブラリの追加
ライブラリの追加は以下のコマンドで行ってください
依存関係を追加した後は、必ず生成された Lock ファイルをコミットしてください。

- フロント: `cd apps/frontend && pnpm add <パッケージ名>`
- バック: `cd apps/backend && poetry add <パッケージ名>`

### ディレクトリ構成
```Plaintext
team4_app/
├── apps/
│   ├── frontend/  # Next.js (React / TypeScript)
│   └── backend/   # FastAPI (Python 3.11)
├── package.json   # モノリポ全体管理
├── turbo.json     # 実行パイプライン設定
└── .tool-versions # 言語バージョン固定ファイル
```

### 環境変数
.env などのファイルは Git 管理外です。

## ❓ 5. 困ったときは
- 「コマンドが見つからない」: mise や poetry のパス設定を確認し、`source ~/.zshrc` を実行してください。
- 「ライブラリのエラーが出る」: `pnpm install:all`を再度実行してください。

## 6. 注意点
- これはAIによって生成したREADMEです。
- 誤りがある可能性もあるので、その場合はPR出してください。


