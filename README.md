# 🚀 京都市 支援金・補助金 自動収集＆閲覧アプリ

本プロジェクト（給付金ナビ）は、京都市の公式ホームページ等から「給付金・助成金・支援金・補助金」に関する情報を自動で収集し、**ユーザーのプロフィール（世帯構成、所得、就労状況など）の条件に合致する制度のみを的確に判定・表示する**Webアプリケーションです。

---

## 🌟 【ポートフォリオとしての公開にあたって】
本リポジトリは、チーム開発における成果物を個人的な実績としてForkしたものです。
私は本プロジェクトにおいて、**ユーザープロフィール機能の設計・実装**、および**バックエンドのデータ収集（ETL）パイプラインの構築**を主導しました。

**💡 主な担当領域とアピールポイント**
- **プロフィール機能とマッチング基盤の構築:** ユーザーの属性（世帯構成、所得、就労状況等）をフロントエンドから受け取り、バックエンドでマッチング可能な形式に変換・構造化して保存するAPIとデータベース設計を実装。
- **ハイブリッド検索エンジンの実装:** Google Search APIの制限回避のため、`DuckDuckGo` と `Tavily Search API` を併用（二刀流）した堅牢な自動収集システムを構築。
- **LLM（OpenAI）による高精度な情報抽出:** プロンプトを網羅性優先にチューニングし、ノイズを弾きつつ制度概要をMarkdown形式で自動生成。
- **開発効率の向上:** 無駄なAPI通信を削減するためのローカルキャッシュ機構（JSON保存）を導入。

---

## 📸 アプリケーションの動作イメージ

**▼ ① ユーザープロフィール入力画面**
ユーザーの生活状況を入力。バックエンド側で、制度の受給条件と照合・マッチング可能なデータ形式へ適切に変換し、構造化して保存しています。
![プロフィール入力画面](./images/profile-input.png)

**▼ ② パーソナライズされた検索結果（マッチング）画面**
スクレイピングパイプラインで自動収集した実際の給付金データの中から、上記のプロフィール条件に合致する制度を判定・抽出して表示します。
![検索結果画面](./images/search-results.png)

---

## 🛠 開発環境と技術スタック
- **Frontend:** Next.js (React / TypeScript)
- **Backend:** FastAPI (Python 3.12)
- **Data Pipeline:** OpenAI API, Tavily Search API, DuckDuckGo Search, BeautifulSoup
- **Package Manager:** pnpm, Poetry, mise

---

このプロジェクトは、**Next.js (フロントエンド)** と **FastAPI (バックエンド)** を組み合わせたモノリポ構成です。

Dockerを使わずに、チーム全体の開発環境（ランタイム・ライブラリ）を完全に一致させる仕組みを採用しています。

以下簡単にセットアップの方法を記載しています。

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


