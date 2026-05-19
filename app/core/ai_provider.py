from groq import Groq
from app.core.config import settings

class GroqProvider:

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)

    def chat(self, prompt: str):
        response = self.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

ai_provider = GroqProvider()
