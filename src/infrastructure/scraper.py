import os
import re
import time
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from typing import List
from src.domain.models import JobOffer

class CloudWorksScraper:
    def fetch_jobs(self, category_id: int, category_name: str) -> List[JobOffer]:
        # URL設定
        if category_id:
            url = f"https://crowdworks.jp/public/jobs?category_id={category_id}&order=new"
        else:
            url = "https://crowdworks.jp/public/jobs?order=new"
            
        job_offers = []

        with sync_playwright() as p:
            # ブラウザ起動（動きを確認するために headless=False にしています）
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
            
            # Cookieのセット
            raw_cookie = os.getenv("BROWSER_COOKIE")
            if raw_cookie:
                cookies = []
                for item in raw_cookie.split(";"):
                    if "=" in item:
                        name, value = item.strip().split("=", 1)
                        cookies.append({
                            "name": name, 
                            "value": value, 
                            "domain": "crowdworks.jp", 
                            "path": "/"
                        })
                context.add_cookies(cookies)

            page = context.new_page()

            try:
                print(f"  [Playwright] Accessing: {url}...")
                page.goto(url, wait_until="domcontentloaded")
                
                # 案件が表示されるまで少し待機
                time.sleep(3)

                # HTMLを解析
                content = page.content()
                soup = BeautifulSoup(content, "html.parser")
                
                # 「/public/jobs/数字」という形式のリンクをすべて探す
                links = soup.find_all("a", href=re.compile(r"/public/jobs/\d+"))
                
                print(f"  [Debug] ページ内から {len(links)} 個のリンクを発見しました")

                for a in links:
                    href = a.get("href")
                    # ID部分（数字のみ）を抽出
                    match = re.search(r"/public/jobs/(\d+)", href)
                    if not match: continue
                    job_id = match.group(1)

                    # 重複排除（同じ案件のリンクが複数あるため）
                    if any(j.job_id == job_id for j in job_offers): continue

                    # タイトル取得（リンクのテキストか、親の見出しから取得）
                    title = a.get_text(strip=True)
                    if len(title) < 5:
                        parent = a.find_parent(["h3", "div", "span"])
                        if parent:
                            title = parent.get_text(strip=True).split('\n')[0]
                    
                    if len(title) < 5: continue

                    job_offers.append(JobOffer(
                        job_id=job_id,
                        category=category_name,
                        title=title[:80],
                        reward="詳細はサイト内",
                        url="https://crowdworks.jp" + href if href.startswith("/") else href
                    ))

                print(f"  [Debug] 有効な案件を {len(job_offers)} 件抽出しました")

            except Exception as e:
                print(f"  [!] エラーが発生しました: {e}")
            finally:
                browser.close()

        return job_offers