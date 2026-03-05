import logging
from pathlib import Path

from app.config import settings
from app.formats.base import get_handler
from app.llm.base import get_provider
from app.worker.celery_app import celery_app

import app.formats.plaintext  # noqa: F401
import app.formats.csv_handler  # noqa: F401
import app.formats.docx_handler  # noqa: F401
import app.formats.xlsx_handler  # noqa: F401
import app.formats.pptx_handler  # noqa: F401
import app.llm.openai_provider  # noqa: F401
import app.llm.azure_openai_provider  # noqa: F401
import app.llm.google_provider  # noqa: F401

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name="translate_file")
def translate_file(
    self,
    session_token: str,
    job_id: str,
    filename: str,
    source_lang: str,
    target_lang: str,
    instructions: str | None = None,
) -> dict:
    data_dir = Path(settings.data_dir)
    job_dir = data_dir / session_token / job_id
    input_path = job_dir / f"input{Path(filename).suffix}"
    output_path = job_dir / f"output{Path(filename).suffix}"

    try:
        self.update_state(state="PROCESSING")

        glossary = None
        glossary_path = data_dir / session_token / "glossary.csv"
        if glossary_path.exists():
            glossary = glossary_path.read_text(encoding="utf-8")

        handler = get_handler(filename)
        segments = handler.extract_texts(input_path)

        if not segments:
            handler.replace_texts(input_path, [], output_path)
            return {"status": "completed", "filename": filename}

        provider = get_provider(settings.llm_provider)
        translated = provider.translate(segments, source_lang, target_lang, instructions, glossary)

        handler.replace_texts(input_path, translated, output_path)

        return {"status": "completed", "filename": filename}

    except Exception as e:
        logger.exception(f"Translation failed for job {job_id}")
        raise

    finally:
        if input_path.exists():
            input_path.unlink()
