import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

from backend.api import main as api_main
from backend.services.ai.session_service import SessionService
from backend.services.ai.chat_history_service import ChatHistoryService
from backend.services.ai.chat_service import ChatService


class DummyLLMService:
    """Minimal LLM service for testing"""

    def generate_chat_response(self, messages):
        class R:
            success = True
            content = "Hello!"
            model_used = "dummy-model"
            tokens_used = 1
            response_time = 0.01
            metadata = {}
        return R()

    async def stream_chat_response(self, context, timeout=60):
        yield "Hello"
        yield "!"


def init_db(path: str) -> None:
    """Create tables used by session and history services."""
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE chat_sessions (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            model_id TEXT NOT NULL,
            user_id TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            message_count INTEGER DEFAULT 0,
            is_archived BOOLEAN DEFAULT FALSE,
            metadata TEXT DEFAULT '{}'
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE chat_messages (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            model_id TEXT,
            tokens_used INTEGER,
            response_time REAL,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
        )
        """
    )
    conn.commit()
    conn.close()


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(str(db_path))

    session_service = SessionService(db_path=str(db_path))
    history_service = ChatHistoryService(db_path=str(db_path))
    llm = DummyLLMService()
    api_main.session_service = session_service
    api_main.chat_history_service = history_service
    api_main.chat_service = ChatService(llm, session_service, history_service)

    return TestClient(api_main.app)


def test_send_chat_message(client):
    resp = client.post(
        "/api/chat/sessions",
        json={"title": "Test", "model_id": "dummy-model", "user_id": "u1"},
    )
    assert resp.status_code == 200
    session_id = resp.json()["id"]

    resp = client.post(
        "/api/chat/send",
        json={"session_id": session_id, "message": "Hi", "user_id": "u1"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["content"] == "Hello!"


def test_stream_chat_message(client):
    session = client.post(
        "/api/chat/sessions",
        json={"title": "Stream", "model_id": "dummy-model"},
    ).json()
    with client.stream(
        "POST",
        "/api/chat/stream",
        json={"session_id": session["id"], "message": "Hi"},
    ) as resp:
        body = b"".join(resp.iter_bytes()).decode()
    assert "Hello" in body


def test_session_crud(client):
    resp = client.post(
        "/api/chat/sessions",
        json={"title": "CRUD", "model_id": "dummy-model", "user_id": "user"},
    )
    assert resp.status_code == 200
    session = resp.json()
    sid = session["id"]

    resp = client.get("/api/chat/sessions")
    assert any(s["id"] == sid for s in resp.json())

    resp = client.get(f"/api/chat/sessions/{sid}")
    assert resp.json()["id"] == sid

    resp = client.put(
        f"/api/chat/sessions/{sid}",
        json={"title": "Updated"},
    )
    assert resp.status_code == 200

    resp = client.get(f"/api/chat/sessions/{sid}")
    assert resp.json()["title"] == "Updated"

    resp = client.delete(f"/api/chat/sessions/{sid}")
    assert resp.status_code == 200

    resp = client.get(f"/api/chat/sessions/{sid}")
    assert resp.status_code == 404
