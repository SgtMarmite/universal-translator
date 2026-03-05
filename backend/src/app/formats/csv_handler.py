import csv
from pathlib import Path

from app.formats.base import FormatHandler, register
from app.models.job import TextSegment


@register([".csv"])
class CsvHandler(FormatHandler):
    def extract_texts(self, file_path: Path) -> list[TextSegment]:
        segments = []
        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader):
                for col, value in row.items():
                    if value and value.strip() and not self._is_numeric(value.strip()):
                        segments.append(TextSegment(
                            id=f"{col}:{row_idx}",
                            text=value.strip(),
                            context=f"Column: {col}",
                            metadata={"column": col, "row": row_idx},
                        ))
        return segments

    def replace_texts(self, file_path: Path, translated: list[TextSegment], output_path: Path) -> None:
        lookup = {seg.id: seg.text for seg in translated}

        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)

        for row_idx, row in enumerate(rows):
            for col in row:
                key = f"{col}:{row_idx}"
                if key in lookup:
                    row[col] = lookup[key]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def _is_numeric(value: str) -> bool:
        try:
            float(value)
            return True
        except ValueError:
            return False
