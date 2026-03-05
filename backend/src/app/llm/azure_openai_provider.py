from openai import AzureOpenAI

from app.config import settings
from app.llm.base import LLMProvider, register_provider


@register_provider("azure_openai")
class AzureOpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            api_version="2024-12-01-preview",
        )
        self.deployment = settings.azure_openai_deployment

    def _call_api(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return response.choices[0].message.content
