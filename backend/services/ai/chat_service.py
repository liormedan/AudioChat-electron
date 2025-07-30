import logging
import time
from typing import List
from datetime import datetime

from backend.models import Message, ChatResponse, ModelNotAvailableError, SessionNotFoundError
from typing import TYPE_CHECKING

from .session_service import SessionService
from .chat_history_service import ChatHistoryService

if TYPE_CHECKING:
    from backend.services.ai.llm_service import LLMService

logger = logging.getLogger(__name__)


class ChatService:
    """High level chat orchestration"""

    def __init__(self, llm_service: "LLMService", session_service: SessionService, history_service: ChatHistoryService):
        self.llm_service = llm_service
        self.session_service = session_service
        self.history_service = history_service

    def _build_context(self, session_id: str, limit: int = 10) -> List[dict]:
        messages = self.history_service.get_session_messages(session_id, limit=limit)
        return [{"role": m.role, "content": m.content} for m in messages]

    def send_message(self, session_id: str, message: str, user_id: str = None) -> ChatResponse:
        session = self.session_service.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            raise SessionNotFoundError(f"Session {session_id} not found")

        context = self._build_context(session_id)
        context.append({"role": "user", "content": message})

        start = time.time()
        provider_resp = self.llm_service.generate_chat_response(context)
        if not provider_resp or not provider_resp.success:
            error_msg = provider_resp.error_message if provider_resp else "no response"
            logger.error(f"LLM generation failed: {error_msg}")
            raise ModelNotAvailableError(error_msg)

        elapsed = time.time() - start
        response = ChatResponse(
            content=provider_resp.content,
            model_id=provider_resp.model_used,
            tokens_used=provider_resp.tokens_used,
            response_time=elapsed,
            success=True,
            metadata=provider_resp.metadata,
        )

        user_msg = Message(
            id="",
            session_id=session_id,
            role="user",
            content=message,
            timestamp=datetime.utcnow(),
        )
        self.history_service.save_message(session_id, user_msg)

        ai_msg = Message(
            id="",
            session_id=session_id,
            role="assistant",
            content=response.content,
            timestamp=datetime.utcnow(),
            model_id=provider_resp.model_used,
            tokens_used=provider_resp.tokens_used,
            response_time=provider_resp.response_time,
        )
        self.history_service.save_message(session_id, ai_msg)

        self.session_service.increment_message_count(session_id, 2)
        return response
