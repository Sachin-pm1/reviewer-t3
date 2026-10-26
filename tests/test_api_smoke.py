"""API smoke test via ASGI transport (offline — no /analyze, no model download)."""

from __future__ import annotations


async def test_health_reports_ai_disabled(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["ai_enabled"] is False  # no key in tests


async def test_source_types_catalog(client):
    resp = await client.get("/source-types")
    assert resp.status_code == 200
    assert "file_csv" in resp.json()


async def test_project_and_source_crud(client, sample_csv_path):
    created = await client.post(
        "/projects", json={"name": "Spotify", "product_name": "Spotify"}
    )
    assert created.status_code == 201
    project_id = created.json()["id"]

    src = await client.post(
        f"/projects/{project_id}/sources",
        json={"source_type": "file_csv", "config": {"path": sample_csv_path}},
    )
    assert src.status_code == 201

    detail = await client.get(f"/projects/{project_id}")
    assert detail.status_code == 200
    assert len(detail.json()["sources"]) == 1


async def test_bad_source_config_is_422(client):
    created = await client.post(
        "/projects", json={"name": "X", "product_name": "X"}
    )
    project_id = created.json()["id"]
    resp = await client.post(
        f"/projects/{project_id}/sources",
        json={"source_type": "file_csv", "config": {"path": "/missing.csv"}},
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "validation_error"


async def test_unknown_job_is_404(client):
    resp = await client.get("/jobs/does-not-exist")
    assert resp.status_code == 404


async def test_reviews_endpoint_empty_for_new_project(client):
    created = await client.post("/projects", json={"name": "R", "product_name": "R"})
    project_id = created.json()["id"]
    resp = await client.get(f"/projects/{project_id}/reviews")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_report_types_catalog(client):
    resp = await client.get("/report-types")
    assert resp.status_code == 200
    assert {"executive", "prd", "roadmap"} <= set(resp.json())
