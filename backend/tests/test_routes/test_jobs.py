import os
from pathlib import Path


def test_list_jobs_empty(client):
    client.get("/api/session")
    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert response.json()["jobs"] == []


def test_list_jobs_no_session(client):
    response = client.get("/api/jobs")
    assert response.status_code == 401


def test_download_nonexistent_job(client):
    client.get("/api/session")
    response = client.get("/api/jobs/nonexistent/download")
    assert response.status_code == 404


def test_delete_nonexistent_job(client):
    client.get("/api/session")
    response = client.delete("/api/jobs/nonexistent")
    assert response.status_code == 404
