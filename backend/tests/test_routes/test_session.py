def test_get_session_creates_cookie(client):
    response = client.get("/api/session")
    assert response.status_code == 200
    data = response.json()
    assert data["session_active"] is True
    assert ".txt" in data["formats"]
    assert "english" in data["languages"]
    assert "auto" in data["languages"]
    assert "session_token" in response.cookies


def test_get_session_returns_all_formats(client):
    response = client.get("/api/session")
    data = response.json()
    expected_exts = [".txt", ".csv", ".docx", ".xlsx", ".pptx"]
    for ext in expected_exts:
        assert ext in data["formats"]
