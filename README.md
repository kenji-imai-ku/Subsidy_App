# 🚀 Team4 App モノリポ開発ガイド

このプロジェクトは、**Next.js (フロントエンド)** と **FastAPI (バックエンド)** を組み合わせたモノリポ構成です。
Dockerを使わずに、チーム全体の開発環境（ランタイム・ライブラリ）を完全に一致させる仕組みを採用しています。

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

リポジトリをクローンした後、**ルートディレクトリ**で以下のコマンドを実行してください。

```bash
# 1. 適切な Node.js と Python を自動インストール
mise install

# 2. フロントとバックの依存関係を一括インストール
pnpm install:all
