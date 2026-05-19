import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:

    def __init__(self):

        # ===== AI =====
        self.GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")

        # ===== LINE =====
        self.LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
        self.LINE_USER_ID = os.getenv("LINE_USER_ID")

        # ===== 讀取多個信箱設定 =====
        self.EMAILS = []

        i = 1
        while True:
            address = os.getenv(f"EMAIL_{i}_ADDRESS")
            password = os.getenv(f"EMAIL_{i}_PASSWORD")
            # 讀取信箱別名
            alias = os.getenv(f"EMAIL_{i}_ALIAS")

            if not address:
                break

            if not password:
                raise ValueError(f"EMAIL_{i}_PASSWORD is not set")

            self.EMAILS.append({
                "email": address,
                "password": password,
                # 若 .env 中有設定 ALIAS 則使用，否則自動擷取 @ 前的字串作為預設別名
                "alias": alias if alias else address.split('@')[0]
            })

            i += 1

            if not self.EMAILS:
                raise ValueError("No EMAIL accounts configured")

settings = Settings()
