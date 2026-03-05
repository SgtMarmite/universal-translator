import os
from pathlib import Path
from unittest.mock import patch, MagicMock


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


@patch("app.routes.translate.translate_file")
def test_upload_valid_file(mock_task, client, data_dir):
    mock_result = MagicMock()
    mock_result.id = "test-task-id"
    mock_task.delay.return_value = mock_result

    client.get("/api/session")
    response = client.post(
        "/api/translate",
        files={"file": ("test.txt", b"hello world", "text/plain")},
        data={"source_lang": "english", "target_lang": "german", "instructions": "be formal"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["status"] == "queued"
    assert "job_id" in data

    mock_task.delay.assert_called_once()
    call_kwargs = mock_task.delay.call_args.kwargs
    assert call_kwargs["filename"] == "test.txt"
    assert call_kwargs["source_lang"] == "english"
    assert call_kwargs["target_lang"] == "german"
    assert call_kwargs["instructions"] == "be formal"
