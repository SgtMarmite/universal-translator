from pathlib import Path
import tempfile

from app.formats.csv_handler import CsvHandler
from app.models.job import TextSegment


def test_extract_texts():
    handler = CsvHandler()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("name,age,city\nAlice,30,New York\nBob,25,Berlin\n")
        f.flush()

        segments = handler.extract_texts(Path(f.name))

    text_values = [s.text for s in segments]
    assert "Alice" in text_values
    assert "New York" in text_values
    assert "Bob" in text_values
    assert "Berlin" in text_values
    # age column is numeric, should not be extracted
    assert "30" not in text_values

    Path(f.name).unlink()


def test_replace_texts():
    handler = CsvHandler()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        f.write("name,city\nAlice,New York\n")
        f.flush()
        input_path = Path(f.name)

    translated = [
        TextSegment(id="name:0", text="Alisa"),
        TextSegment(id="city:0", text="Nowy Jork"),
    ]

    output_path = input_path.parent / "output.csv"
    handler.replace_texts(input_path, translated, output_path)

    content = output_path.read_text()
    assert "Alisa" in content
    assert "Nowy Jork" in content

    output_path.unlink()
    input_path.unlink()
