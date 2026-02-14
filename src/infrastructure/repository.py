import gspread
from src.domain.models import JobOffer

class GoogleSheetsRepository:
    """スプレッドシートへの保存と重複チェックを担当するクラス"""
    
    def __init__(self, credentials_path: str, sheet_id: str):
        # 認証設定
        self.gc = gspread.service_account(filename=credentials_path)
        self.sh = self.gc.open_by_key(sheet_id)
        
        # get_worksheet(0) ではなく、シート名で直接指定します
        try:
            self.worksheet = self.sh.worksheet("案件情報")
        except gspread.exceptions.WorksheetNotFound:
            # もし「案件情報」という名前のシートが見つからない場合、
            # 安全のために一番左のシートを使います
            self.worksheet = self.sh.get_worksheet(0)
            print("  [!] 警告: '案件情報'シートが見つからないため、最初のシートを使用します。")

    def is_duplicated(self, job_id: str) -> bool:
        """すでにスプレッドシートに存在するIDかどうかを確認"""
        # 1列目(ID列)をすべて取得してチェック
        existing_ids = self.worksheet.col_values(1)
        return job_id in existing_ids

    def save(self, job: JobOffer):
        """案件情報をスプレッドシートの末尾に追加"""
        self.worksheet.append_row(job.to_list())