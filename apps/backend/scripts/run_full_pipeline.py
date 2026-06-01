import subprocess
import sys
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="収集からDB登録までを一括実行します")
    parser.add_argument("--dry-run", action="store_true", help="DB登録を行わず、抽出結果の表示のみ行います")
    parser.add_argument("--limit", type=int, default=100, help="取得するユニークURLの最大数 (default: 100)")
    args = parser.parse_args()

    # スクリプトの場所から apps/backend ディレクトリを特定
    backend_dir = Path(__file__).resolve().parent.parent
    
    print("\n" + "="*60)
    print(f"🚀 Step 1: 支援制度情報の収集・Markdown変換を開始します... (上限: {args.limit}件)")
    print("="*60)
    
    # 1. スクレイパーの実行
    scraper_cmd = [sys.executable, "scraper_pipeline.py", "--limit", str(args.limit)]
    try:
        subprocess.run(scraper_cmd, cwd=backend_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Step 1 (Scraper) でエラーが発生しました。処理を中断します。: {e}")
        sys.exit(1)

    print("\n" + "="*60)
    print("📥 Step 2: 抽出されたMarkdownを構造化してDBへ登録を開始します...")
    print("="*60)

    # 2. インポーターの実行
    import_cmd = [sys.executable, "scripts/import_programs_from_markdown.py"]
    if args.dry_run:
        import_cmd.append("--dry-run")
    
    try:
        subprocess.run(import_cmd, cwd=backend_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Step 2 (Importer) でエラーが発生しました。: {e}")
        sys.exit(1)

    print("\n" + "="*60)
    print("✅ すべての工程が正常に完了しました！")
    print("="*60)

if __name__ == "__main__":
    main()
