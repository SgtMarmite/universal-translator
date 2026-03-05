from abc import ABC, abstractmethod
from pathlib import Path

from app.models.job import TextSegment

HANDLERS: dict[str, type["FormatHandler"]] = {}


def register(extensions: list[str]):
    def decorator(cls: type["FormatHandler"]):
        for ext in extensions:
            HANDLERS[ext.lower()] = cls
        return cls
    return decorator


def get_handler(filename: str) -> "FormatHandler":
    ext = Path(filename).suffix.lower()
    handler_cls = HANDLERS.get(ext)
    if not handler_cls:
        raise ValueError(f"Unsupported file format: {ext}")
    return handler_cls()


class FormatHandler(ABC):
    @abstractmethod
    def extract_texts(self, file_path: Path) -> list[TextSegment]:
        ...

    @abstractmethod
    def replace_texts(self, file_path: Path, translated: list[TextSegment], output_path: Path) -> None:
        ...
