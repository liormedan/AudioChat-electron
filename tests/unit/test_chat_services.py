import os
import unittest
from tempfile import TemporaryDirectory
from datetime import datetime

from backend.services.ai.chat_service import ChatService
from backend.services.ai.session_service import SessionService
from backend.services.ai.chat_history_service import ChatHistoryService
from backend.models import Message, MessageRole
from dataclasses import dataclass, field


@dataclass
class DummyResponse:
    content: str
    tokens_used: int
    cost: float
    response_time: float
    model_used: str
    success: bool = True
    error_message: str = ""
    metadata: dict = field(default_factory=dict)


class DummyLLMService:
    def __init__(self):
        # do not call parent init
        pass

    def generate_chat_response(self, messages):
        return DummyResponse(
            content="pong",
            tokens_used=1,
            cost=0.0,
            response_time=0.01,
            model_used="dummy",
            success=True,
        )


class ChatServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        db_path = os.path.join(self.temp_dir.name, "chat.db")
        self.session_service = SessionService(db_path)
        self.history_service = ChatHistoryService(db_path)
        self.llm_service = DummyLLMService()
        self.chat_service = ChatService(self.llm_service, self.session_service, self.history_service)
        self.session = self.session_service.create_session(title="test", model_id="dummy")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_and_get_session(self):
        fetched = self.session_service.get_session(self.session.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.title, "test")

    def test_save_and_load_messages(self):
        msg = Message(id="1", session_id=self.session.id, role="user", content="hi", timestamp=datetime.utcnow())
        self.history_service.save_message(self.session.id, msg)
        msgs = self.history_service.get_session_messages(self.session.id)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].content, "hi")

    def test_send_message(self):
        response = self.chat_service.send_message(self.session.id, "ping")
        self.assertTrue(response.success)
        msgs = self.history_service.get_session_messages(self.session.id)
        self.assertEqual(len(msgs), 2)  # user + assistant
        self.assertEqual(msgs[1].role, MessageRole.ASSISTANT)


if __name__ == "__main__":
    unittest.main()
