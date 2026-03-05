from google import genai

from app.config import settings
from app.llm.base import LLMProvider, register_provider


@register_provider("google")
class GoogleProvider(LLMProvider):
    def __init__(self):
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model = settings.google_model

    def _call_api(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        return response.text
