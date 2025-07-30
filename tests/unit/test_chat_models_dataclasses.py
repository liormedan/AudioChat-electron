from datetime import datetime

from backend.models import ChatSession, Message, ChatResponse, MessageRole, MessageType


def test_chat_session_roundtrip():
    now = datetime.now()
    session = ChatSession(
        id="s1",
        title="Title",
        model_id="model-1",
        user_id=None,
        created_at=now,
        updated_at=now,
        message_count=0,
    )
    data = session.to_dict()
    restored = ChatSession.from_dict(data)
    assert restored == session


def test_message_roundtrip_defaults():
    now = datetime.utcnow()
    msg = Message(
        id="m1",
        session_id="s1",
        content="hi",
        timestamp=now,
    )
    assert msg.role == MessageRole.USER
    assert msg.type == MessageType.TEXT
    data = msg.to_dict()
    restored = Message.from_dict(data)
    assert restored == msg


def test_chat_response_roundtrip():
    resp = ChatResponse(
        content="ok",
        model_id="model",
        tokens_used=1,
        response_time=0.1,
        success=True,
    )
    data = resp.to_dict()
    restored = ChatResponse.from_dict(data)
    assert restored == resp

