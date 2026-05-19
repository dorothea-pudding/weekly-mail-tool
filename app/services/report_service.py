from app.core.ai_provider import ai_provider

class ReportService:

    def generate(self, important_emails):

        combined_text = "\n\n".join(important_emails)

        prompt = f"""
            你是一個資訊整理專家。

            請將以下重要郵件整理成週報。

            輸出格式必須包含：

            【本週重要事項】
            - 條列重點

            【需要處理的事項】
            - 條列待辦

            【截止日期彙整】
            - 若無則寫 無

            【風險提醒】
            - 若無則寫 無

            內容要：
            - 精簡
            - 不超過 400 字
            - 使用繁體中文

            郵件內容：
            {combined_text}
            """

        return ai_provider.chat(prompt)
