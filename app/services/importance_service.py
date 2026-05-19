import json
import re
from app.core.ai_provider import GroqProvider

ai_provider = GroqProvider()

class ImportanceService:

    def analyze(self, email_text):
        # 避免 token 爆掉
        email_text = email_text[:3000]

        #prompt可以根據個人需求修改
        prompt = f"""
            請判斷以下郵件的重要性。

            只允許回傳 JSON，不能有任何多餘文字：

            {{
            "important": true 或 false,
            "title": "重要事件簡短標題 (例如：校務系統主機維護)",
            "summary": "一句話總結郵件重點",
            "requires_action": true 或 false (是否需要收件人採取行動，例如繳費、確認資訊等),
            "action_item": "需採取的具體行動說明 (若 requires_action 為 false 則填空字串)"
            }}

            郵件內容：
            {email_text}
            """

        try:
            response = ai_provider.chat(prompt)

            # 使用非貪婪模式抽出 JSON
            match = re.search(r"\{.*?\}", response, re.DOTALL)
            if not match:
                return {"important": False}

            json_str = match.group()
            data = json.loads(json_str)

            # 確保重要欄位存在
            if "important" not in data:
                 return {"important": False}

            return data

        except json.JSONDecodeError as e:
            print(f"JSON 解析錯誤: {e}")
            return {"important": False}
        except Exception as e:
            print(f"AI 模組錯誤: {e}")
            return {"important": False}
