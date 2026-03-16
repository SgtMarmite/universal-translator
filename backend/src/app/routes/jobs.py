import json
import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from app.config import settings

router = APIRouter(prefix="/api")


def _get_session_or_401(request: Request) -> str:
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="No session")
    return token


@router.get("/jobs")
def list_jobs(request: Request):
    session_token = _get_session_or_401(request)
    session_dir = Path(settings.data_dir) / session_token

    if not session_dir.exists():
        return {"jobs": []}

    jobs = []
    for job_dir in sorted(session_dir.iterdir()):
        if not job_dir.is_dir() or job_dir.name == "glossary.csv":
            continue

        job_id = job_dir.name

        original_name_path = job_dir / "original_filename"
        original_name = original_name_path.read_text().strip() if original_name_path.exists() else "unknown"

        output_files = list(job_dir.glob("output.*"))
        error_path = job_dir / "error"

        if error_path.exists():
            status = "failed"
            error = error_path.read_text().strip()
        elif output_files:
            status = "completed"
            error = None
        else:
            status = "processing"
            error = None

        review = None
        review_path = job_dir / "review.json"
        if review_path.exists():
            try:
                review = json.loads(review_path.read_text())
            except json.JSONDecodeError:
                pass

        jobs.append({
            "job_id": job_id,
            "status": status,
            "filename": original_name,
            "error": error,
            "review": review,
        })

    return {"jobs": jobs}


@router.get("/jobs/{job_id}/download")
def download_job(job_id: str, request: Request):
    session_token = _get_session_or_401(request)
    job_dir = Path(settings.data_dir) / session_token / job_id

    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")

    output_files = list(job_dir.glob("output.*"))
    if not output_files:
        raise HTTPException(status_code=404, detail="Translation not ready")

    output_file = output_files[0]
    original_name_path = job_dir / "original_filename"
    download_name = original_name_path.read_text().strip() if original_name_path.exists() else f"translated{output_file.suffix}"

    return FileResponse(
        path=str(output_file),
        filename=download_name,
        media_type="application/octet-stream",
    )


@router.delete("/jobs/{job_id}")
def delete_job(job_id: str, request: Request):
    session_token = _get_session_or_401(request)
    job_dir = Path(settings.data_dir) / session_token / job_id

    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")

    shutil.rmtree(job_dir, ignore_errors=True)
    return {"status": "ok", "message": "Job removed"}
