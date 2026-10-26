"""Auth is pure DB + crypto logic (no Claude/Spotify calls), so this runs
entirely at the HTTP layer — no fakes needed, no reason to test it any other
way. Covers the two real bugs found auditing this right after building it:
bcrypt's 72-byte password limit crashing signup, and GET /me/taste returning
200-with-defaults instead of 404 for an account that never saved a profile
(which silently skipped the taste-setup screen client-side).
"""

from __future__ import annotations

import itertools

# All tests in this file share one SQLite file for the whole run (see
# conftest.py) — a literal default email here would let an earlier test's
# leftover account collide with a later one and mask a real bug (e.g. a
# "duplicate email" test that accidentally 409s on its *first* call too,
# for the wrong reason, and still looks green). A counter makes every
# unqualified call unique regardless of test order.
_email_counter = itertools.count()


def _unique_email() -> str:
    return f"listener{next(_email_counter)}@example.com"


async def _signup(client, email=None, password="correcthorse123"):
    return await client.post(
        "/auth/signup", json={"email": email or _unique_email(), "password": password}
    )


async def test_signup_creates_account_and_returns_token(client):
    email = _unique_email()
    resp = await _signup(client, email=email)
    assert resp.status_code == 201
    body = resp.json()
    assert body["user"]["email"] == email
    assert body["access_token"]
    assert body["token_type"] == "bearer"


async def test_signup_duplicate_email_is_409(client):
    email = _unique_email()
    await _signup(client, email=email)
    resp = await _signup(client, email=email)
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "conflict"


async def test_signup_duplicate_email_is_case_insensitive(client):
    await _signup(client, email="Listener@Example.com")
    resp = await _signup(client, email="listener@example.com")
    assert resp.status_code == 409


async def test_signup_password_too_short_is_422(client):
    resp = await _signup(client, password="short")
    assert resp.status_code == 422


async def test_signup_password_over_72_bytes_is_422_not_500(client):
    # Reproduced directly: bcrypt.hashpw raises ValueError past 72 bytes rather
    # than truncating, so without validation at the boundary this crashed
    # signup as a raw 500 instead of a clean, actionable error.
    resp = await _signup(client, password="a" * 100)
    assert resp.status_code == 422


async def test_signin_wrong_password_is_401(client):
    email = _unique_email()
    await _signup(client, email=email)
    resp = await client.post(
        "/auth/signin", json={"email": email, "password": "wrongpassword"}
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthorized"


async def test_signin_unknown_email_gives_the_same_error_as_wrong_password(client):
    # Deliberately identical to the wrong-password case — a login form
    # shouldn't confirm which emails have accounts.
    resp = await client.post(
        "/auth/signin", json={"email": "nobody@example.com", "password": "whatever123"}
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthorized"


async def test_signin_with_correct_credentials_returns_token(client):
    email = _unique_email()
    await _signup(client, email=email)
    resp = await client.post(
        "/auth/signin", json={"email": email, "password": "correcthorse123"}
    )
    assert resp.status_code == 200
    assert resp.json()["access_token"]


async def test_signin_password_over_72_bytes_is_401_not_500(client):
    # verify_password() catches bcrypt's ValueError on an overlong *attempt*,
    # independent of the signup-side fix above — a too-long guess must fail
    # cleanly, not crash.
    email = _unique_email()
    await _signup(client, email=email)
    resp = await client.post(
        "/auth/signin", json={"email": email, "password": "a" * 100}
    )
    assert resp.status_code == 401


async def test_me_without_token_is_401(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_me_with_garbage_token_is_401(client):
    resp = await client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert resp.status_code == 401


async def test_me_with_valid_token_returns_the_signed_up_user(client):
    email = _unique_email()
    signup = await _signup(client, email=email)
    token = signup.json()["access_token"]
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == email


async def test_taste_profile_is_404_before_it_is_ever_saved(client):
    signup = await _signup(client)
    token = signup.json()["access_token"]
    resp = await client.get("/me/taste", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


async def test_taste_profile_requires_auth(client):
    resp = await client.get("/me/taste")
    assert resp.status_code == 401
    resp = await client.put("/me/taste", json={"seed_artists": [], "seed_genres": [], "novelty": 50})
    assert resp.status_code == 401


async def test_taste_profile_put_then_get_round_trips(client):
    signup = await _signup(client)
    token = signup.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    put_resp = await client.put(
        "/me/taste",
        json={"seed_artists": ["Radiohead"], "seed_genres": ["alternative"], "novelty": 75},
        headers=headers,
    )
    assert put_resp.status_code == 200

    get_resp = await client.get("/me/taste", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json() == {
        "seed_artists": ["Radiohead"],
        "seed_genres": ["alternative"],
        "novelty": 75,
    }


async def test_taste_profile_is_scoped_per_account(client):
    a = (await _signup(client, email="a@example.com")).json()["access_token"]
    b = (await _signup(client, email="b@example.com")).json()["access_token"]

    await client.put(
        "/me/taste",
        json={"seed_artists": ["Artist A"], "seed_genres": [], "novelty": 40},
        headers={"Authorization": f"Bearer {a}"},
    )

    # B never saved a profile — must still be 404, not see A's.
    b_resp = await client.get("/me/taste", headers={"Authorization": f"Bearer {b}"})
    assert b_resp.status_code == 404
