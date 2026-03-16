import json
import logging
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Response, UploadFile, Form

from app.agents.pipeline import run_translation
from app.config import settings
from app.formats.base import get_handler
from app.models.session import SUPPORTED_FORMATS
from app.routes.session import ensure_session_token

import app.formats.plaintext  # noqa: F401
import app.formats.csv_handler  # noqa: F401
import app.formats.docx_handler  # noqa: F401
import app.formats.xlsx_handler  # noqa: F401
import app.formats.pptx_handler  # noqa: F401

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


@router.post("/translate")
async def upload_and_translate(
    request: Request,
    response: Response,
    file: UploadFile,
    source_lang: str = Form(...),
    target_lang: str = Form(...),
    instructions: str = Form(default=""),
):
    session_token = ensure_session_token(request, response)

    ext = Path(file.filename).suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {ext}")

    content = await file.read()
    max_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max: {settings.max_file_size_mb}MB")

    job_id = uuid.uuid4().hex
    job_dir = Path(settings.data_dir) / session_token / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    input_path = job_dir / f"input{ext}"
    input_path.write_bytes(content)
    (job_dir / "original_filename").write_text(file.filename)

    try:
        handler = get_handler(file.filename)
        segments = handler.extract_texts(input_path)

        if not segments:
            output_path = job_dir / f"output{ext}"
            handler.replace_texts(input_path, [], output_path)
            return {"job_id": job_id, "filename": file.filename, "status": "completed", "review": None}

        translations = None
        review = None

        async for agent_name, event_type, data in run_translation(
            segments=segments,
            source_lang=source_lang,
            target_lang=target_lang,
            session_token=session_token,
            instructions=instructions or None,
        ):
            if event_type == "done":
                translations = data["translations"]
                review = data["review"]

        if translations:
            output_path = job_dir / f"output{ext}"
            handler.replace_texts(input_path, translations, output_path)

        if review:
            (job_dir / "review.json").write_text(json.dumps(review, ensure_ascii=False))

        return {"job_id": job_id, "filename": file.filename, "status": "completed", "review": review}

    except Exception as e:
        logger.exception(f"Translation failed for job {job_id}")
        (job_dir / "error").write_text(str(e))
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if input_path.exists():
            input_path.unlink()


@router.post("/glossary")
async def upload_glossary(
    request: Request,
    response: Response,
    file: UploadFile,
):
    session_token = ensure_session_token(request, response)

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Glossary must be a CSV file")

    content = await file.read()
    session_dir = Path(settings.data_dir) / session_token
    session_dir.mkdir(parents=True, exist_ok=True)
    glossary_path = session_dir / "glossary.csv"
    glossary_path.write_bytes(content)

    return {"status": "ok", "message": "Glossary uploaded"}


@router.delete("/glossary")
async def delete_glossary(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="No session")

    glossary_path = Path(settings.data_dir) / session_token / "glossary.csv"
    if glossary_path.exists():
        glossary_path.unlink()

    return {"status": "ok", "message": "Glossary removed"}
