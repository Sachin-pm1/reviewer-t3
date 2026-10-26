"""Regression tests for the copilot chat history gap.

ChatService.ask() always persisted a ChatSession row (proved directly against the
live app's real sqlite file — the rows were there), but there was no GET endpoint to
read them back and the frontend only ever kept messages in React state. Reload the
page or switch tabs and the conversation vanished, which reads to a user as "it isn't
storing" even though the write path always worked. These tests cover the read side
that was actually missing: a history endpoint, scoped per project, in order.
"""

from __future__ import annotations

from app.analysis.provider.claude_service import ClaudeService
from app.chat.service import ChatService
from app.products.schemas import ProjectCreate
from app.products.service import ProjectService
from tests._fakes import FakeProvider


def _chat_service(session) -> ChatService:
    return ChatService(session, claude_service=ClaudeService(provider=FakeProvider()))


async def test_chat_history_starts_empty_for_a_new_project(client):
    created = await client.post("/projects", json={"name": "Spotify", "product_name": "Spotify"})
    project_id = created.json()["id"]

    resp = await client.get(f"/projects/{project_id}/chat")
    assert resp.status_code == 200
    assert resp.json() == []


async def test_asking_persists_and_shows_up_in_history(db_session):
    project = await ProjectService(db_session).create_project(
        ProjectCreate(name="Spotify", product_name="Spotify")
    )
    await db_session.commit()

    svc = _chat_service(db_session)
    response = await svc.ask(project.id, "Why are users unhappy?")
    await db_session.commit()

    history = await svc.history(project.id)
    assert len(history) == 1
    assert history[0].question == "Why are users unhappy?"
    assert history[0].answer == response.answer
    assert history[0].id == response.session_id


async def test_history_is_scoped_to_its_project(db_session):
    projects = ProjectService(db_session)
    a = await projects.create_project(ProjectCreate(name="A", product_name="A"))
    b = await projects.create_project(ProjectCreate(name="B", product_name="B"))
    await db_session.commit()

    svc = _chat_service(db_session)
    await svc.ask(a.id, "Question about A")
    await db_session.commit()

    assert len(await svc.history(a.id)) == 1
    assert await svc.history(b.id) == []


async def test_history_is_returned_oldest_first(db_session):
    project = await ProjectService(db_session).create_project(
        ProjectCreate(name="Spotify", product_name="Spotify")
    )
    await db_session.commit()

    svc = _chat_service(db_session)
    await svc.ask(project.id, "First question")
    await db_session.commit()
    await svc.ask(project.id, "Second question")
    await db_session.commit()

    history = await svc.history(project.id)
    assert [h.question for h in history] == ["First question", "Second question"]
