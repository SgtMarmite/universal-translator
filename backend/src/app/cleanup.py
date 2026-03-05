import logging
import shutil
import time
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


def cleanup_expired_files() -> int:
    data_dir = Path(settings.data_dir)
    if not data_dir.exists():
        return 0

    now = time.time()
    removed = 0

    for session_dir in data_dir.iterdir():
        if not session_dir.is_dir():
            continue
        for job_dir in session_dir.iterdir():
            if not job_dir.is_dir():
                continue
            age = now - job_dir.stat().st_mtime
            if age > settings.file_ttl_seconds:
                shutil.rmtree(job_dir)
                removed += 1
                logger.info(f"Cleaned up expired job dir: {job_dir}")

        # remove empty session dirs
        if session_dir.is_dir() and not any(session_dir.iterdir()):
            session_dir.rmdir()

    return removed
