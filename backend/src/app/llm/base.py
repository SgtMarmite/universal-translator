import json
import logging
import time
from abc import ABC, abstractmethod

from app.models.job import TextSegment

logger = logging.getLogger(__name__)

PROVIDERS: dict[str, type["LLMProvider"]] = {}


def register_provider(name: str):
    def decorator(cls: type["LLMProvider"]):
        PROVIDERS[name] = cls
        return cls
    return decorator


def get_provider(name: str) -> "LLMProvider":
    provider_cls = PROVIDERS.get(name)
    if not provider_cls:
        raise ValueError(f"Unknown LLM provider: {name}. Available: {list(PROVIDERS.keys())}")
    return provider_cls()


def build_prompt(
    segments: list[TextSegment],
    source_lang: str,
    target_lang: str,
    instructions: str | None = None,
    glossary: str | None = None,
) -> str:
    source = "auto-detect the source language" if source_lang == "auto" else source_lang

    parts = [f"Translate the following texts from {source} to {target_lang}."]

    if instructions:
        parts.append(f"\nCustom instructions: {instructions}")

    if glossary:
        parts.append(f"\nGlossary (always use these exact translations):\n{glossary}")

    parts.append("\nReturn ONLY a JSON array of translated strings in the same order.")
    parts.append("Do not translate proper nouns, code, or formulas.")
    parts.append("Preserve any leading/trailing whitespace from the original.\n")

    for i, seg in enumerate(segments):
        context_hint = f" (context: {seg.context})" if seg.context else ""
        parts.append(f"[{i}] \"{seg.text}\"{context_hint}")

    return "\n".join(parts)


def parse_response(response_text: str, expected_count: int) -> list[str]:
    text = response_text.strip()
    start = text.find("[")
    end = text.rfind("]") + 1
    if start == -1 or end == 0:
        raise ValueError(f"Could not find JSON array in LLM response: {text[:200]}")
    result = json.loads(text[start:end])
    if len(result) != expected_count:
        raise ValueError(f"Expected {expected_count} translations, got {len(result)}")
    return result


MAX_BATCH_SIZE = 50
MAX_RETRIES = 3


class LLMProvider(ABC):
    @abstractmethod
    def _call_api(self, prompt: str) -> str:
        ...

    def translate(
        self,
        segments: list[TextSegment],
        source_lang: str,
        target_lang: str,
        instructions: str | None = None,
        glossary: str | None = None,
    ) -> list[TextSegment]:
        all_translated = []

        for i in range(0, len(segments), MAX_BATCH_SIZE):
            batch = segments[i:i + MAX_BATCH_SIZE]
            prompt = build_prompt(batch, source_lang, target_lang, instructions, glossary)
            translated_texts = self._call_with_retry(prompt, len(batch))

            for seg, translated_text in zip(batch, translated_texts):
                all_translated.append(TextSegment(
                    id=seg.id,
                    text=translated_text,
                    context=seg.context,
                    metadata=seg.metadata,
                ))

        return all_translated

    def _call_with_retry(self, prompt: str, expected_count: int) -> list[str]:
        for attempt in range(MAX_RETRIES):
            try:
                response = self._call_api(prompt)
                return parse_response(response, expected_count)
            except Exception:
                if attempt == MAX_RETRIES - 1:
                    raise
                wait = 2 ** attempt
                logger.warning(f"LLM call failed (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {wait}s")
                time.sleep(wait)
        raise RuntimeError("Unreachable")
