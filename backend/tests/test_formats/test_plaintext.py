from pathlib import Path
import tempfile

from app.formats.plaintext import PlainTextHandler
from app.models.job import TextSegment


def test_extract_texts():
    handler = PlainTextHandler()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Hello world\n\nThis is a test\n\nThird paragraph")
        f.flush()

        segments = handler.extract_texts(Path(f.name))

    assert len(segments) == 3
    assert segments[0].text == "Hello world"
    assert segments[1].text == "This is a test"
    assert segments[2].text == "Third paragraph"


def test_replace_texts():
    handler = PlainTextHandler()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("Hello world\n\nThis is a test")
        f.flush()
        input_path = Path(f.name)

    translated = [
        TextSegment(id="0", text="Hallo Welt"),
        TextSegment(id="1", text="Das ist ein Test"),
    ]

    output_path = input_path.parent / "output.txt"
    handler.replace_texts(input_path, translated, output_path)

    result = output_path.read_text()
    assert "Hallo Welt" in result
    assert "Das ist ein Test" in result

    output_path.unlink()
    input_path.unlink()


def test_empty_file():
    handler = PlainTextHandler()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("")
        f.flush()

        segments = handler.extract_texts(Path(f.name))

    assert len(segments) == 0
    Path(f.name).unlink()
