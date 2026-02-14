import requests
import json

class DiscordNotifier:
    """Discord Webhookを使用してメッセージを送信するクラス"""

    def __init__(self, webhook_url: str):
        """
        Args:
            webhook_url (str): .envから読み込んだDiscordのURL
        """
        self.webhook_url = webhook_url

    def send(self, message: str) -> bool:
        """
        Discordにメッセージを送信する
        
        Args:
            message (str): 送信するテキスト内容
        Returns:
            bool: 送信成功ならTrue、失敗ならFalse
        """
        payload = {"content": message}
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(
                self.webhook_url, 
                data=json.dumps(payload), 
                headers=headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Discordへの通知に失敗しました: {e}")
            return False