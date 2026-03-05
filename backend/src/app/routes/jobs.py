import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from app.config import settings
from app.worker.celery_app import celery_app

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
        status = "unknown"
        filename = ""
        error = None

        original_name_path = job_dir / "original_filename"
        original_name = original_name_path.read_text().strip() if original_name_path.exists() else "unknown"

        output_files = list(job_dir.glob("output.*"))

        if output_files:
            status = "completed"
            filename = original_name
        else:
            status = "processing"
            filename = original_name

        # check celery task state for more accurate status
        task_info_path = job_dir / "task_id"
        if task_info_path.exists():
            task_id = task_info_path.read_text().strip()
            result = celery_app.AsyncResult(task_id)
            if result.state == "PENDING":
                status = "queued"
            elif result.state == "PROCESSING" or result.state == "STARTED":
                status = "processing"
            elif result.state == "SUCCESS":
                status = "completed"
            elif result.state == "FAILURE":
                status = "failed"
                error = str(result.result) if result.result else "Translation failed"

        jobs.append({
            "job_id": job_id,
            "status": status,
            "filename": filename,
            "error": error,
        })

    return {"jobs": jobs}


@router.get("/jobs/{job_id}")
def get_job(job_id: str, request: Request):
    session_token = _get_session_or_401(request)
    job_dir = Path(settings.data_dir) / session_token / job_id

    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")

    output_files = list(job_dir.glob("output.*"))
    status = "completed" if output_files else "processing"

    return {
        "job_id": job_id,
        "status": status,
        "has_output": bool(output_files),
    }


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
        background=_cleanup_after_download(job_dir),
    )


def _cleanup_after_download(job_dir: Path):
    from starlette.background import BackgroundTask
    return BackgroundTask(shutil.rmtree, job_dir, ignore_errors=True)


@router.delete("/jobs/{job_id}")
def delete_job(job_id: str, request: Request):
    session_token = _get_session_or_401(request)
    job_dir = Path(settings.data_dir) / session_token / job_id

    if not job_dir.exists():
        raise HTTPException(status_code=404, detail="Job not found")

    shutil.rmtree(job_dir, ignore_errors=True)
    return {"status": "ok", "message": "Job removed"}
