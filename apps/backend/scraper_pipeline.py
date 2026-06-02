import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from openai import OpenAI
import time
import json
import os
import re
import argparse
from dotenv import load_dotenv
from ddgs import DDGS
from tavily import TavilyClient
import hashlib

# --- DB Imports ---
from app.core.database import SessionLocal
from app.models.program_source import ProgramSource

# .envファイルから環境変数を読み込む
load_dotenv()

# ==========================================
# 設定エリア
# ==========================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("環境変数 OPENAI_API_KEY が設定されていません。.envファイルを確認してください。")

if not TAVILY_API_KEY:
    raise ValueError("環境変数 TAVILY_API_KEY が設定されていません。.envファイルを確認してください。")

# OpenAIクライアントの初期化
client = OpenAI(api_key=OPENAI_API_KEY)

# ==========================================
# 関数定義
# ==========================================

def get_registered_urls():
    """
    データベースから既に登録済みのURLを取得する
    """
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
    """
    DuckDuckGoを使用してURLを取得する
    """
    print(f"DuckDuckGoを使用してURLを取得中: {query}")
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=num_results))
            return [r['href'] for r in results]
    except Exception as e:
        print(f"DuckDuckGo検索中にエラーが発生しました: {e}")
        return []

def get_urls_from_tavily(query, num_results=50):
    """
    Tavily APIを使用してURLを取得する
    """
    print(f"Tavily APIを使用してURLを取得中: {query}")
    try:
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)
        response = tavily_client.search(query=query, max_results=num_results)
        return [result["url"] for result in response.get("results", [])]
    except Exception as e:
        print(f"Tavily検索中にエラーが発生しました（スキップします）: {e}")
        return []

def get_page_summary(url):
    """
    Step 1: 軽量スクレイピング（ヘッダー情報取得）
    """
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
            
        return {
            "title": title.strip() if title else "",
            "description": description.strip() if description else ""
        }
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {"title": "", "description": ""}

def judge_support_program(title, description, client):
    """
    Step 2: OpenAI APIによる判定
    """
    if not title and not description:
        return {"is_target": False, "reason": "No content to judge"}

    print("Judging program relevance using OpenAI API...")
    
    prompt = f"""あなたは支援制度の判定AIです。タイトルと概要から、支援制度に関するページか判定し、以下のJSONフォーマットのみを出力してください。
    * is_target (boolean): 支援制度なら true、関係ないページなら false
    * support_type (string): cash, subsidy, medical, service_discount, service_dispatch, loan, goods, consultation, tax_reduction, other の中から最適なものを選択。対象外の場合は null。
    * reason (string): 判定理由

【判定ルール】
* データ収集の網羅性を最優先します。受付期間が終了している可能性があったり、対象者が限定的であったりしても、少しでも「給付金・助成金・支援金・補助金・手当・減免・サービス提供」という制度の概要を説明しているページであれば、必ず is_target: true として抽出してください。
* 議事録、入札情報、単なるニュースリリース、市役所へのアクセス案内など、「明らかに制度の説明ページではないノイズ」と断言できる場合のみ is_target: false にしてください。
* 判定に迷った場合は、網羅性を重視して is_target: true としてください。

タイトル: {title}
概要: {description}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a support program analyzer. Return only JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={ "type": "json_object" }
    )
    
    result = json.loads(response.choices[0].message.content)
    return result

def extract_markdown(url):
    """
    Step 3: 対象ページのみのMarkdown化
    """
    print(f"Extracting Markdown content from: {url}")
    time.sleep(1)
    
    try:
        response = requests.get(url, timeout=10)
        response.encoding = response.apparent_encoding
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        body = soup.find('body')
        if not body:
            return ""
        
        # 不要なタグを削除
        for tag in body.find_all(['script', 'style', 'header', 'footer', 'nav']):
            tag.decompose()
            
        # Markdownに変換
        markdown_content = md(str(body))
        
        # 前後の不要な空白行を整理
        markdown_content = markdown_content.strip()
        # 連続する空行を整理
        markdown_content = re.sub(r'\n\s*\n', '\n\n', markdown_content)
        
        return markdown_content
    except Exception as e:
        print(f"Error extracting markdown from {url}: {e}")
        return ""

def main():
    """
    Step 4: メイン処理 (main) と ファイル出力
    """
    parser = argparse.ArgumentParser(description="支援制度情報収集パイプライン")
    parser.add_argument("--limit", type=int, default=100, help="取得するユニークURLの最大数 (default: 100)")
    args = parser.parse_args()

    # 出力ディレクトリの作成
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 検索キーワードの抜本的な拡充（網羅性を担保する13ワード）
    base_keywords = [
        "給付", "助成", "補助", "手当",      # お金（直接的）
        "支給", "交付",                    # お金（事務的）
        "減免", "免除", "負担軽減",         # 負担を減らす
        "貸付", "融資",                    # お金を借りる
        "生活支援", "サービス提供"          # サービス・生活
    ]
    
    domain = "www.city.kyoto.lg.jp"
    queries = [f"site:{domain} {kw}" for kw in base_keywords]
    
    cache_file = "search_cache.json"
    
    # キャッシュのチェック
    unique_urls = set()
    if os.path.exists(cache_file):
        print("キャッシュからURLを読み込みました")
        with open(cache_file, "r", encoding="utf-8") as f:
            cached_urls = json.load(f)
            for url in cached_urls:
                unique_urls.add(url)
    
    registered_urls = get_registered_urls()
    print(f"DB登録済みのURL {len(registered_urls)} 件をスキップ対象として読み込みました。")

    # 指定された数に足りない場合のみ新規検索を実行
    if len(unique_urls) < args.limit:
        print(f"現在の候補数 ({len(unique_urls)}件) が上限 ({args.limit}件) 未満のため、新規検索を開始します...")

        for query in queries:
            if len(unique_urls) >= args.limit:
                print(f"指定された上限 ({args.limit}件) に達したため、検索を終了します。")
                break
                
            # 1. DuckDuckGo検索
            ddg_urls = get_urls_from_search(query, num_results=20)
            for url in ddg_urls:
                if url in registered_urls:
                    continue
                unique_urls.add(url)
                if len(unique_urls) >= args.limit:
                    break
            
            if len(unique_urls) >= args.limit:
                break

            # 2. Tavily検索
            tavily_urls = get_urls_from_tavily(query, num_results=20)
            for url in tavily_urls:
                if url in registered_urls:
                    continue
                unique_urls.add(url)
                if len(unique_urls) >= args.limit:
                    break
            
            # APIへの負荷軽減
            time.sleep(1)
    
    # 最終的なリストを確定
    target_urls = list(unique_urls)
    if len(target_urls) > args.limit:
        target_urls = target_urls[:args.limit]
        
    print(f"収集完了: 処理対象のユニークURL数 = {len(target_urls)}")
    
    # キャッシュに保存
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(target_urls, f, ensure_ascii=False, indent=4)
    
    for url in target_urls:
        try:
            # Step 1: 概要取得
            summary = get_page_summary(url)
            title = summary["title"]
            description = summary["description"]
            
            # Step 2: 判定
            judgment = judge_support_program(title, description, client)
            is_target = judgment.get("is_target", False)
            support_type = judgment.get("support_type")
            reason = judgment.get("reason", "")
            
            if not is_target:
                print(f"Result: [SKIP] {url} (Reason: {reason})")
                continue
            
            print(f"Result: [MATCH] {url} (Type: {support_type})")
            
            # Step 3: Markdown抽出
            markdown_content = extract_markdown(url)
            
            # Step 4: ファイル出力
            filename_match = re.search(r'([^/]+)\.html$', url)
            if filename_match:
                filename = filename_match.group(1)
            else:
                filename = hashlib.md5(url.encode()).hexdigest()[:10]
                
            file_path = os.path.join(output_dir, f"{filename}.md")
            
            output_text = f"""URL: {url}
Title: {title}
Support Type: {support_type}
Reason: {reason}

---

{markdown_content}
"""
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(output_text)
                
            print(f"Successfully saved to: {file_path}")
            
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")

if __name__ == "__main__":
    main()
