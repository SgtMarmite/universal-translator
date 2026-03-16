import json
import logging

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

from app.agents.prompts import (
    CONTEXT_AGENT_PROMPT,
    TRANSLATOR_AGENT_PROMPT,
    REVIEWER_AGENT_PROMPT,
)
from app.agents.tools import load_glossary, load_source_texts
from app.config import settings
from app.models.job import TextSegment

logger = logging.getLogger(__name__)

KEY_ENRICHED_CONTEXT = "enriched_context"
KEY_TRANSLATIONS = "translations"
KEY_REVIEW = "review_result"

context_agent = LlmAgent(
    name="ContextAgent",
    model=settings.google_model,
    instruction=CONTEXT_AGENT_PROMPT,
    description="Analyzes source texts, loads glossary, and produces a context brief for translation.",
    tools=[load_glossary, load_source_texts],
    output_key=KEY_ENRICHED_CONTEXT,
)

translator_agent = LlmAgent(
    name="TranslatorAgent",
    model=settings.google_model,
    instruction=TRANSLATOR_AGENT_PROMPT,
    description="Translates text segments using the enriched context from the previous step.",
    tools=[load_source_texts],
    output_key=KEY_TRANSLATIONS,
)

reviewer_agent = LlmAgent(
    name="ReviewerAgent",
    model=settings.google_model,
    instruction=REVIEWER_AGENT_PROMPT,
    description="Reviews translation quality, checking terminology and consistency.",
    output_key=KEY_REVIEW,
)

translation_pipeline = SequentialAgent(
    name="TranslationPipeline",
    sub_agents=[context_agent, translator_agent, reviewer_agent],
    description="End-to-end document translation pipeline with context enrichment and quality review.",
)

APP_NAME = "universal_translator"


async def run_translation(
    segments: list[TextSegment],
    source_lang: str,
    target_lang: str,
    session_token: str,
    instructions: str | None = None,
):
    """Run the ADK translation pipeline and yield events.

    Yields (agent_name, event_type, data) tuples for SSE streaming.
    """
    source_texts_json = json.dumps([s.text for s in segments], ensure_ascii=False)

    initial_state = {
        "source_texts": source_texts_json,
        "source_lang": source_lang,
        "target_lang": target_lang,
        "session_token": session_token,
        "data_dir": settings.data_dir,
        "custom_instructions": instructions or "",
    }

    runner = InMemoryRunner(agent=translation_pipeline, app_name=APP_NAME)
    session = await runner.session_service.create_session(
        app_name=APP_NAME,
        user_id=session_token,
        state=initial_state,
    )

    user_message = (
        f"Translate the following document segments from {source_lang} to {target_lang}.\n"
        f"Session token: {session_token}\n"
        f"Data directory: {settings.data_dir}\n"
    )
    if instructions:
        user_message += f"Custom instructions: {instructions}\n"
    user_message += f"\nSource texts:\n{source_texts_json}"

    content = UserContent(parts=[Part(text=user_message)])

    last_agent = None
    translations_raw = None
    review_raw = None

    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        agent_name = event.author
        if agent_name and agent_name != last_agent:
            if last_agent:
                yield last_agent, "agent_completed", {}
            yield agent_name, "agent_started", {}
            last_agent = agent_name

        if event.is_final_response() and event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    if agent_name == "TranslatorAgent":
                        translations_raw = part.text
                    elif agent_name == "ReviewerAgent":
                        review_raw = part.text

    if last_agent:
        yield last_agent, "agent_completed", {}

    session_state = (await runner.session_service.get_session(
        app_name=APP_NAME,
        user_id=session.user_id,
        session_id=session.id,
    )).state

    translations_raw = translations_raw or session_state.get(KEY_TRANSLATIONS, "[]")
    review_raw = review_raw or session_state.get(KEY_REVIEW, "{}")

    translated_texts = _parse_translations(translations_raw, len(segments))
    translated_segments = []
    for seg, text in zip(segments, translated_texts):
        translated_segments.append(TextSegment(id=seg.id, text=text, context=seg.context, metadata=seg.metadata))

    review = _parse_review(review_raw)

    yield "pipeline", "done", {"translations": translated_segments, "review": review}


def _parse_translations(raw: str, expected_count: int) -> list[str]:
    text = raw.strip()
    start = text.find("[")
    end = text.rfind("]") + 1
    if start == -1 or end == 0:
        logger.error(f"Could not find JSON array in translator output: {text[:200]}")
        raise ValueError("Translator did not return a valid JSON array")
    result = json.loads(text[start:end])
    if len(result) != expected_count:
        raise ValueError(f"Expected {expected_count} translations, got {len(result)}")
    return result


def _parse_review(raw: str) -> dict:
    text = raw.strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        return {"score": 0, "status": "error", "issues": [], "summary": "Review parsing failed"}
    try:
        return json.loads(text[start:end])
    except json.JSONDecodeError:
        return {"score": 0, "status": "error", "issues": [], "summary": "Review parsing failed"}
