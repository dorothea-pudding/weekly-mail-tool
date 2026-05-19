import requests
from app.core.config import settings

class LineService:

    def push(self, user_id, message):
        url = "https://api.line.me/v2/bot/message/push"

        headers = {
            "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        # 避免 LINE 訊息長度超過 5000 字元的官方限制 (保險起見設定在 4500)
        if len(message) > 4500:
            message = message[:4500] + "\n... [Message truncated due to length limit]"

        payload = {
            "to": user_id,
            "messages": [{
                "type": "text",
                "text": message
            }]
        }

        try:
            # 加上 timeout (10秒) 避免網路異常時程式無窮等待
            response = requests.post(url, headers=headers, json=payload, timeout=10)

            print(f"LINE push status code: {response.status_code}")
            
            # 只有在狀態碼不是 200 (成功) 時，才印出詳細錯誤回應來除錯
            if response.status_code != 200:
                print(f"LINE API error response: {response.text}")

            return response.status_code == 200

        except requests.exceptions.RequestException as e:
            # 捕捉斷網、DNS 解析失敗等網路層級的錯誤
            print(f"Network error during LINE push: {e}")
            return False
