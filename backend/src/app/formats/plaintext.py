from pathlib import Path

from app.formats.base import FormatHandler, register
from app.models.job import TextSegment


@register([".txt"])
class PlainTextHandler(FormatHandler):
    def extract_texts(self, file_path: Path) -> list[TextSegment]:
        content = file_path.read_text(encoding="utf-8")
        paragraphs = content.split("\n\n")
        segments = []
        for i, para in enumerate(paragraphs):
            stripped = para.strip()
            if stripped:
                segments.append(TextSegment(id=str(i), text=stripped))
        return segments

    def replace_texts(self, file_path: Path, translated: list[TextSegment], output_path: Path) -> None:
        content = file_path.read_text(encoding="utf-8")
        paragraphs = content.split("\n\n")
        lookup = {seg.id: seg.text for seg in translated}

        result = []
        for i, para in enumerate(paragraphs):
            if para.strip() and str(i) in lookup:
                result.append(lookup[str(i)])
            else:
                result.append(para)

        output_path.write_text("\n\n".join(result), encoding="utf-8")
