import logging
import time
import uuid
from typing import List, AsyncGenerator
from datetime import datetime

from backend.models.chat import Message, ChatResponse, ModelNotAvailableError, SessionNotFoundError
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

    async def stream_message(self, session_id: str, message: str, user_id: str = None) -> AsyncGenerator[str, None]:
        """
        Send message with streaming response
        
        Args:
            session_id (str): Session ID
            message (str): User message
            user_id (str, optional): User ID
            
        Yields:
            str: Streaming response chunks
            
        Raises:
            SessionNotFoundError: If session not found
            ModelNotAvailableError: If model not available
        """
        session = self.session_service.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            raise SessionNotFoundError(f"Session {session_id} not found")

        context = self._build_context(session_id)
        context.append({"role": "user", "content": message})

        # Save user message immediately
        user_msg = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role="user",
            content=message,
            timestamp=datetime.utcnow(),
        )
        self.history_service.save_message(session_id, user_msg)

        # Stream AI response
        start_time = time.time()
        full_response = ""
        tokens_used = 0
        
        try:
            # Check if LLM service supports streaming
            if hasattr(self.llm_service, 'stream_chat_response'):
                async for chunk in self.llm_service.stream_chat_response(context):
                    full_response += chunk
                    tokens_used += 1  # Approximate token count
                    yield chunk
            else:
                # Fallback to regular response
                provider_resp = self.llm_service.generate_chat_response(context)
                if not provider_resp or not provider_resp.success:
                    error_msg = provider_resp.error_message if provider_resp else "no response"
                    logger.error(f"LLM generation failed: {error_msg}")
                    raise ModelNotAvailableError(error_msg)
                
                full_response = provider_resp.content
                tokens_used = provider_resp.tokens_used
                yield full_response

            # Save AI response
            response_time = time.time() - start_time
            ai_msg = Message(
                id=str(uuid.uuid4()),
                session_id=session_id,
                role="assistant",
                content=full_response,
                timestamp=datetime.utcnow(),
                model_id=session.model_id,
                tokens_used=tokens_used,
                response_time=response_time,
            )
            self.history_service.save_message(session_id, ai_msg)
            self.session_service.increment_message_count(session_id, 1)  # Only increment for AI message
            
        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            raise ModelNotAvailableError(str(e))

    def get_conversation_context(self, session_id: str, max_messages: int = 10) -> List[Message]:
        """
        Get conversation context for a session
        
        Args:
            session_id (str): Session ID
            max_messages (int): Maximum number of messages to retrieve
            
        Returns:
            List[Message]: List of recent messages
        """
        return self.history_service.get_session_messages(session_id, limit=max_messages)
