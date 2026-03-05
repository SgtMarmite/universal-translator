from dataclasses import dataclass, field
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TextSegment:
    id: str
    text: str
    context: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class Job:
    job_id: str
    session_token: str
    filename: str
    source_lang: str
    target_lang: str
    status: JobStatus = JobStatus.QUEUED
    error: str | None = None
    instructions: str | None = None
