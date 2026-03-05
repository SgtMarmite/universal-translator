import pytest

from app.llm.base import build_prompt, parse_response
from app.models.job import TextSegment


def test_build_prompt_basic():
    segments = [
        TextSegment(id="0", text="Hello"),
        TextSegment(id="1", text="World", context="greeting"),
    ]
    prompt = build_prompt(segments, "english", "german")
    assert "english" in prompt
    assert "german" in prompt
    assert '"Hello"' in prompt
    assert '"World"' in prompt
    assert "(context: greeting)" in prompt


def test_build_prompt_auto_detect():
    segments = [TextSegment(id="0", text="Hello")]
    prompt = build_prompt(segments, "auto", "german")
    assert "auto-detect" in prompt


def test_build_prompt_with_instructions():
    segments = [TextSegment(id="0", text="Hello")]
    prompt = build_prompt(segments, "english", "german", instructions="Use formal tone")
    assert "Use formal tone" in prompt


def test_build_prompt_with_glossary():
    segments = [TextSegment(id="0", text="Hello")]
    prompt = build_prompt(segments, "english", "german", glossary="Hello,Hallo")
    assert "Hello,Hallo" in prompt


def test_parse_response_valid():
    result = parse_response('["Hallo", "Welt"]', 2)
    assert result == ["Hallo", "Welt"]


def test_parse_response_with_markdown():
    result = parse_response('```json\n["Hallo", "Welt"]\n```', 2)
    assert result == ["Hallo", "Welt"]


def test_parse_response_wrong_count():
    with pytest.raises(ValueError, match="Expected 2"):
        parse_response('["Hallo"]', 2)


def test_parse_response_invalid_json():
    with pytest.raises(ValueError, match="Could not find"):
        parse_response("not json at all", 2)
