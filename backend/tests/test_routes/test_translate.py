import os
from unittest.mock import patch, AsyncMock


def test_upload_unsupported_format(client):
    client.get("/api/session")
    response = client.post(
        "/api/translate",
        files={"file": ("test.pdf", b"content", "application/pdf")},
        data={"source_lang": "english", "target_lang": "german"},
    )
    assert response.status_code == 400
    assert "Unsupported" in response.json()["detail"]


def test_upload_file_too_large(client):
    client.get("/api/session")
    with patch("app.routes.translate.settings") as mock_settings:
        mock_settings.max_file_size_mb = 0
        mock_settings.data_dir = os.environ["DATA_DIR"]
        response = client.post(
            "/api/translate",
            files={"file": ("test.txt", b"hello world", "text/plain")},
            data={"source_lang": "english", "target_lang": "german"},
        )
    assert response.status_code == 400
    assert "too large" in response.json()["detail"]
