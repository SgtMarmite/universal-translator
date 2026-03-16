import json
from pathlib import Path

from google.adk.tools import ToolContext


def load_glossary(session_token: str, data_dir: str, tool_context: ToolContext) -> dict:
    """Loads the user's glossary CSV file if it exists.

    Args:
        session_token: The user's session token for locating their data directory.
        data_dir: The base data directory path.

    Returns:
        dict: Status and glossary content if found.
    """
    glossary_path = Path(data_dir) / session_token / "glossary.csv"
    if glossary_path.exists():
        content = glossary_path.read_text(encoding="utf-8")
        tool_context.state["glossary"] = content
        return {"status": "success", "glossary": content}
    tool_context.state["glossary"] = ""
    return {"status": "no_glossary", "glossary": ""}


def load_source_texts(tool_context: ToolContext) -> dict:
    """Loads source text segments from session state for translation.

    Returns:
        dict: Status and the source texts as a JSON string.
    """
    texts = tool_context.state.get("source_texts", "[]")
    return {"status": "success", "source_texts": texts}
