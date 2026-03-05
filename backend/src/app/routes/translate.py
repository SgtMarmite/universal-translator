import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Response, UploadFile, Form

from app.config import settings
from app.models.session import SUPPORTED_FORMATS
from app.routes.session import ensure_session_token
from app.worker.tasks import translate_file

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

    task = translate_file.delay(
        session_token=session_token,
        job_id=job_id,
        filename=file.filename,
        source_lang=source_lang,
        target_lang=target_lang,
        instructions=instructions or None,
    )

    (job_dir / "task_id").write_text(task.id)
    (job_dir / "original_filename").write_text(file.filename)

    return {
        "job_id": job_id,
        "task_id": task.id,
        "filename": file.filename,
        "status": "queued",
    }


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
