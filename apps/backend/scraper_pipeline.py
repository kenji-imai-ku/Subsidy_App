import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from openai import OpenAI
import time
import json
import os
import re
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
from ddgs import DDGS
from tavily import TavilyClient
import hashlib

# --- Path Setup ---
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

# --- DB and Service Imports ---
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.program_source import ProgramSource
from scripts.import_programs_from_markdown import process_file

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAIクライアントの初期化
client = OpenAI(api_key=settings.openai_api_key)

# ==========================================
# 関数定義
# ==========================================

def get_registered_urls():
    """データベースから既に登録済みのURLを取得する"""
    db = SessionLocal()
    try:
        urls = db.query(ProgramSource.source_url).all()
        return set(url[0] for url in urls)
    except Exception as e:
        print(f"DBからのURL取得中にエラーが発生しました: {e}")
        return set()
    finally:
        db.close()

def get_urls_from_search(query, num_results=50):
    """DuckDuckGoを使用してURLを取得する"""
    print(f"DuckDuckGoを使用してURLを取得中: {query}")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
            return [r['href'] for r in results]
    except Exception as e:
        print(f"DuckDuckGo検索中にエラーが発生しました: {e}")
        return []

def get_urls_from_tavily(query, num_results=50):
    """Tavily APIを使用してURLを取得する"""
    print(f"Tavily APIを使用してURLを取得中: {query}")
    try:
        tavily_client = TavilyClient(api_key=settings.tavily_api_key)
        response = tavily_client.search(query=query, max_results=num_results)
        return [result["url"] for result in response.get("results", [])]
    except Exception as e:
        print(f"Tavily検索中にエラーが発生しました（スキップします）: {e}")
        return []

def get_page_summary(url):
    """軽量スクレイピング（ヘッダー情報取得）"""
    print(f"Processing summary for: {url}")
    time.sleep(1)
    try:
        response = requests.get(url, timeout=10)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else ""
        description = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            content = meta_desc.get('content', "")
            description = " ".join(content) if isinstance(content, list) else str(content)
        return {"title": title.strip() if title else "", "description": description.strip() if description else ""}
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {"title": "", "description": ""}

def judge_support_program(title, description, client):
    """OpenAI APIによる判定"""
    if not title and not description:
        return {"is_target": False, "reason": "No content to judge"}
    print("Judging program relevance using OpenAI API...")
    prompt = f"""あなたは支援制度の判定AIです。タイトルと概要から、支援制度に関するページか判定し、以下のJSONフォーマットのみを出力してください。
    * is_target (boolean): 支援制度なら true、関係ないページなら false
    * support_type (string): cash, subsidy, medical, service_discount, service_dispatch, loan, goods, consultation, tax_reduction, other の中から最適なものを選択。対象外の場合は null。
    * reason (string): 判定理由

【判定ルール】
* データ収集の網羅性を最優先します。少しでも「給付金・助成金・支援金・補助金・手当・減免・サービス提供」という制度の概要を説明しているページであれば、必ず is_target: true として抽出してください。
* 判定に迷った場合は、網羅性を重視して is_target: true としてください。

タイトル: {title}
概要: {description}"""

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You are a support program analyzer. Return only JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)

def extract_markdown(url):
    """対象ページのみのMarkdown化"""
    print(f"Extracting Markdown content from: {url}")
    time.sleep(1)
    try:
        response = requests.get(url, timeout=10)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.find('body')
        if not body: return ""
        for tag in body.find_all(['script', 'style', 'header', 'footer', 'nav']): tag.decompose()
        markdown_content = md(str(body))
        markdown_content = markdown_content.strip()
        markdown_content = re.sub(r'\n\s*\n', '\n\n', markdown_content)
        return markdown_content
    except Exception as e:
        print(f"Error extracting markdown from {url}: {e}")
        return ""

def process_single_url(url, client, db, dry_run):
    """1つのURLを処理（判定 -> Markdown化 -> DB登録）まで完結させる"""
    summary = get_page_summary(url)
    judgment = judge_support_program(summary["title"], summary["description"], client)
    
    if not judgment.get("is_target", False):
        print(f"Result: [SKIP] {url} (Reason: {judgment.get('reason')})")
        return False

    print(f"Result: [MATCH] {url} (Type: {judgment.get('support_type')})")
    markdown_content = extract_markdown(url)
    
    # 一時的にMarkdownを保存
    filename = re.search(r'([^/]+)\.html$', url).group(1) if re.search(r'([^/]+)\.html$', url) else hashlib.md5(url.encode()).hexdigest()[:10]
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    temp_file = output_dir / f"{filename}.md"
    
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\nTitle: {summary['title']}\nSupport Type: {judgment.get('support_type')}\nReason: {judgment.get('reason')}\n\n---\n\n{markdown_content}")
    
    # 即座にインポーターを呼び出す
    success, message = process_file(temp_file, client, db, dry_run)
    if success:
        print(f"    [+] {message}")
    else:
        print(f"    [!] {message}")
    return success

def main():
    parser = argparse.ArgumentParser(description="支援制度情報収集・登録パイプライン (逐次処理対応)")
    parser.add_argument("--limit", type=int, default=100, help="取得する合計ユニークURLの最大数")
    parser.add_argument("--batch-size", type=int, default=10, help="1回に検索・処理するURLの数")
    parser.add_argument("--dry-run", action="store_true", help="DB登録を行わず、抽出結果の表示のみ")
    args = parser.parse_args()

    # テーブルの自動作成
    from app.core.database import engine, Base
    Base.metadata.create_all(bind=engine)

    base_keywords = ["給付", "助成", "補助", "手当", "支給", "交付", "減免", "免除", "負担軽減", "貸付", "融資", "生活支援", "サービス提供"]
    domain = "www.city.kyoto.lg.jp"
    queries = [f"site:{domain} {kw}" for kw in base_keywords]
    
    db = SessionLocal()
    processed_count = 0
    total_found_urls = set()
    
    print(f"[*] 逐次処理を開始します (合計目標: {args.limit}件, 1バッチ: {args.batch_size}件)")

    for query in queries:
        if processed_count >= args.limit: break
        
        # 既に登録済みのURLを再取得
        registered_urls = get_registered_urls()
        
        # 1. 検索してバッチサイズ分の新しいURLを見つける
        print(f"\n--- キーワード検索中: {query} ---")
        new_urls_in_batch = []
        search_results = get_urls_from_search(query, num_results=50) + get_urls_from_tavily(query, num_results=20)
        
        for url in search_results:
            if url not in registered_urls and url not in total_found_urls:
                new_urls_in_batch.append(url)
                total_found_urls.add(url)
                if len(new_urls_in_batch) >= args.batch_size:
                    break
        
        if not new_urls_in_batch:
            print("新しいURLが見つかりませんでした。次のキーワードへ...")
            continue

        # 2. 見つかったバッチを即座に処理
        print(f"[*] {len(new_urls_in_batch)}件の新しいURLを処理します...")
        for url in new_urls_in_batch:
            if processed_count >= args.limit: break
            if process_single_url(url, client, db, args.dry_run):
                processed_count += 1
            time.sleep(1) # レートリミット対策

    print(f"\n[✅] 処理が完了しました。合計登録数: {processed_count}")
    db.close()

if __name__ == "__main__":
    main()
