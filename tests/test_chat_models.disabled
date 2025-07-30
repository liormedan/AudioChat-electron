from datetime import datetime
from backend.models.chat import ChatSession, Message, ChatResponse


def test_chat_session_serialization():
    now = datetime.now()
    session = ChatSession(
        id="s1",
        title="Test Session",
        model_id="model-1",
        user_id="user-123",
        created_at=now,
        updated_at=now,
        message_count=3,
        is_archived=True,
        metadata={"foo": "bar"},
    )

    data = session.to_dict()
    assert data["id"] == "s1"
    assert data["created_at"] == now.isoformat()
    restored = ChatSession.from_dict(data)
    assert restored == session


def test_message_serialization():
    now = datetime.now()
    msg = Message(
        id="m1",
        session_id="s1",
        role="user",
        content="hello",
        timestamp=now,
        model_id="model-1",
        tokens_used=10,
        response_time=0.4,
        metadata={"a": 1},
    )
    data = msg.to_dict()
    assert data["timestamp"] == now.isoformat()
    restored = Message.from_dict(data)
    assert restored == msg


def test_chat_response_serialization():
    resp = ChatResponse(
        content="hi",
        model_id="model-1",
        tokens_used=5,
        response_time=0.2,
        success=True,
        metadata={"x": "y"},
    )
    data = resp.to_dict()
    assert data["success"] is True
    restored = ChatResponse.from_dict(data)
    assert restored == resp
