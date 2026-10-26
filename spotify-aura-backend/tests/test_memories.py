"""Manual per-day memory notes — plain CRUD scoped to the signed-in account,
independent of the Spotify connection. Runs entirely at the HTTP layer, same
reasoning as test_auth.py: no external calls involved."""

from __future__ import annotations

import itertools

_email_counter = itertools.count()


def _unique_email() -> str:
    return f"memory-writer{next(_email_counter)}@example.com"


async def _signed_up_token(client) -> str:
    resp = await client.post(
        "/auth/signup", json={"email": _unique_email(), "password": "correcthorse123"}
    )
    return resp.json()["access_token"]


async def test_list_memories_empty_by_default(client):
    token = await _signed_up_token(client)
    resp = await client.get("/me/memories", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_memories_requires_auth(client):
    resp = await client.get("/me/memories")
    assert resp.status_code == 401


async def test_create_memory(client):
    token = await _signed_up_token(client)
    resp = await client.post(
        "/me/memories",
        json={"date": "2026-07-04", "note": "Rainy afternoon, read for hours.", "mood": "Reflective"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["date"] == "2026-07-04"
    assert body["note"] == "Rainy afternoon, read for hours."
    assert body["mood"] == "Reflective"
    assert body["id"]
    assert body["created_at"].endswith("Z") or "+00:00" in body["created_at"]


async def test_create_memory_without_mood(client):
    token = await _signed_up_token(client)
    resp = await client.post(
        "/me/memories",
        json={"date": "2026-07-04", "note": "No mood set."},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["mood"] is None


async def test_create_memory_rejects_bad_date_format(client):
    token = await _signed_up_token(client)
    resp = await client.post(
        "/me/memories",
        json={"date": "07/04/2026", "note": "wrong format"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


async def test_posting_same_date_twice_edits_not_duplicates(client):
    token = await _signed_up_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    await client.post("/me/memories", json={"date": "2026-07-04", "note": "first draft"}, headers=headers)
    resp = await client.post(
        "/me/memories", json={"date": "2026-07-04", "note": "edited note"}, headers=headers
    )
    assert resp.status_code == 201
    assert resp.json()["note"] == "edited note"

    listing = await client.get("/me/memories", headers=headers)
    assert len(listing.json()) == 1
    assert listing.json()[0]["note"] == "edited note"


async def test_memories_are_scoped_per_account(client):
    token_a = await _signed_up_token(client)
    token_b = await _signed_up_token(client)

    await client.post(
        "/me/memories",
        json={"date": "2026-07-04", "note": "account A's memory"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    resp_b = await client.get("/me/memories", headers={"Authorization": f"Bearer {token_b}"})
    assert resp_b.json() == []

    resp_a = await client.get("/me/memories", headers={"Authorization": f"Bearer {token_a}"})
    assert len(resp_a.json()) == 1


async def test_delete_memory(client):
    token = await _signed_up_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    created = await client.post(
        "/me/memories", json={"date": "2026-07-04", "note": "to be deleted"}, headers=headers
    )
    memory_id = created.json()["id"]

    resp = await client.delete(f"/me/memories/{memory_id}", headers=headers)
    assert resp.status_code == 204

    listing = await client.get("/me/memories", headers=headers)
    assert listing.json() == []


async def test_delete_memory_from_another_account_is_a_noop(client):
    token_a = await _signed_up_token(client)
    token_b = await _signed_up_token(client)
    created = await client.post(
        "/me/memories",
        json={"date": "2026-07-04", "note": "account A's memory"},
        headers={"Authorization": f"Bearer {token_a}"},
    )
    memory_id = created.json()["id"]

    resp = await client.delete(
        f"/me/memories/{memory_id}", headers={"Authorization": f"Bearer {token_b}"}
    )
    assert resp.status_code == 204  # doesn't leak whether the id exists

    listing = await client.get("/me/memories", headers={"Authorization": f"Bearer {token_a}"})
    assert len(listing.json()) == 1  # account A's memory survives
