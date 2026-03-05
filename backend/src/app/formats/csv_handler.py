from pathlib import Path

import pandas as pd

from app.formats.base import FormatHandler, register
from app.models.job import TextSegment


@register([".csv"])
class CsvHandler(FormatHandler):
    def extract_texts(self, file_path: Path) -> list[TextSegment]:
        df = pd.read_csv(file_path)
        segments = []
        for col in df.columns:
            if df[col].dtype == object:
                for idx, value in df[col].items():
                    if pd.notna(value) and str(value).strip():
                        segments.append(TextSegment(
                            id=f"{col}:{idx}",
                            text=str(value).strip(),
                            context=f"Column: {col}",
                            metadata={"column": col, "row": idx},
                        ))
        return segments

    def replace_texts(self, file_path: Path, translated: list[TextSegment], output_path: Path) -> None:
        df = pd.read_csv(file_path)
        for seg in translated:
            col, idx = seg.id.rsplit(":", 1)
            df.at[int(idx), col] = seg.text
        df.to_csv(output_path, index=False)
