from src.domain.models import JobOffer
from typing import List

class JobFilterUseCase:
    def execute(self, jobs: List[JobOffer]) -> List[JobOffer]:
        return [job for job in jobs if self._is_target(job)]

    def _is_target(self, job: JobOffer) -> bool:
        title = job.title.lower()

        # 1. AI案件（カテゴリ問わず）
        ai_keywords = ["ai活用", "ai使用", "chatgpt", "ai", "gpt", "生成ai"]
        if any(k in title for k in ai_keywords):
            return True

        # 2. タスク系キーワード（カテゴリ判定をゆるくしました）
        task_keywords = ["アンケート", "簡単", "初心者"]
        if any(k in title for k in task_keywords):
            return True

        # 3. ライティング系キーワード（文字単価などの条件）
        writing_keywords = ["初心者歓迎", "文字単価", "記事作成", "執筆"]
        if any(k in title for k in writing_keywords):
            return True

        return False