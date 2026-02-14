from pydantic import BaseModel
from typing import Optional

class JobOffer(BaseModel):
    """クラウドワークスの案件情報を表すドメインモデル"""
    job_id: str
    title: str
    reward: str
    url: str
    category: str

    def to_list(self) -> list:
        """スプレッドシート保存用のリスト形式に変換"""
        return [self.job_id, self.category, self.title, self.reward, self.url]