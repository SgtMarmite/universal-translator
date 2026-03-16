import os
import tempfile

import pytest
from fastapi.testclient import TestClient

os.environ["DATA_DIR"] = tempfile.mkdtemp()
os.environ["SESSION_SECRET"] = "test-secret"
os.environ["GOOGLE_API_KEY"] = "test-key"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "false"

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def data_dir():
    return os.environ["DATA_DIR"]
