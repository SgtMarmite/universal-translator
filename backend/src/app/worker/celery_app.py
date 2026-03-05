from celery import Celery

from app.config import settings

celery_app = Celery(
    "universal_translator",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=settings.file_ttl_seconds,
)

celery_app.autodiscover_tasks(["app.worker"])
