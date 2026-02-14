import os
from dotenv import load_dotenv
from src.infrastructure.scraper import CloudWorksScraper
from src.infrastructure.notifier import DiscordNotifier
from src.infrastructure.repository import GoogleSheetsRepository
from src.usecase.monitor_usecase import JobFilterUseCase

def main():
    load_dotenv()
    
    # 依存性の注入（DI）
    scraper = CloudWorksScraper()
    filter_usecase = JobFilterUseCase()
    notifier = DiscordNotifier(os.getenv("DISCORD_WEBHOOK_URL"))
    # .envに設定した変数名に合わせる、または直接ファイル名を指定
    repo = GoogleSheetsRepository("credentials.json", os.getenv("SHEET_ID"))

    # クラウドワークスの実際のカテゴリID（URLに含まれる数字）に修正
    target_categories = [
        {"id": 154, "name": "writing"},      # ライティング（AI記事作成が多い）
        {"id": 147, "name": "clerical"},     # 事務・作業（AIデータ作成・アンケートが多い）
        {"id": 10,  "name": "development"}   # 開発（AIツール作成・自動化が多い）
    ]

    print("--- 巡回を開始します ---")

    for cat in target_categories:
        print(f"Checking {cat['name']}...")
        jobs = scraper.fetch_jobs(cat["id"], cat["name"])
        # 【追加】実際に何件取得できているか表示
        print(f"--- {len(jobs)}件の案件をネットから拾いました ---")
        matched_jobs = filter_usecase.execute(jobs)

        for job in matched_jobs:
            if not repo.is_duplicated(job.job_id):
                repo.save(job)
                notifier.send(f"【新着】{job.title}\n報酬: {job.reward}\nURL: {job.url}")
                print(f"通知送信: {job.title}")

    print("--- 巡回が完了しました ---")

if __name__ == "__main__":
    main()