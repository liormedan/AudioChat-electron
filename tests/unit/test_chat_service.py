"""
Unit tests for ChatService
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from backend.services.ai.chat_service import ChatService
from backend.services.ai.session_service import SessionService
from backend.services.ai.chat_history_service import ChatHistoryService
from backend.models.chat import ChatSession, Message, ChatResponse, SessionNotFoundError, ModelNotAvailableError


class TestChatService:
    """Test ChatService functionality"""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Mock LLM service"""
        mock = Mock()
        mock.generate_chat_response.return_value = Mock(
            success=True,
            content="Test response",
            model_used="test-model",
            tokens_used=10,
            response_time=1.0,
            metadata={}
        )
        return mock
    
    @pytest.fixture
    def mock_session_service(self):
        """Mock session service"""
        mock = Mock(spec=SessionService)
        mock.get_session.return_value = ChatSession(
            id="test-session",
            title="Test Session",
            model_id="test-model",
            user_id="test-user",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            message_count=0
        )
        return mock
    
    @pytest.fixture
    def mock_history_service(self):
        """Mock history service"""
        mock = Mock(spec=ChatHistoryService)
        mock.get_session_messages.return_value = []
        mock.save_message.return_value = "test-message-id"
        return mock
    
    @pytest.fixture
    def chat_service(self, mock_llm_service, mock_session_service, mock_history_service):
        """Create ChatService instance with mocked dependencies"""
        return ChatService(
            llm_service=mock_llm_service,
            session_service=mock_session_service,
            history_service=mock_history_service
        )
    
    def test_send_message_success(self, chat_service, mock_session_service, mock_history_service, mock_llm_service):
        """Test successful message sending"""
        result = chat_service.send_message("test-session", "Hello", "test-user")
        
        # Verify session was retrieved
        mock_session_service.get_session.assert_called_once_with("test-session")
        
        # Verify LLM was called
        mock_llm_service.generate_chat_response.assert_called_once()
        
        # Verify messages were saved
        assert mock_history_service.save_message.call_count == 2  # User + AI message
        
        # Verify message count was incremented
        mock_session_service.increment_message_count.assert_called_once_with("test-session", 2)
        
        # Verify response
        assert isinstance(result, ChatResponse)
        assert result.success is True
        assert result.content == "Test response"
        assert result.model_id == "test-model"
    
    def test_send_message_session_not_found(self, chat_service, mock_session_service):
        """Test sending message to non-existent session"""
        mock_session_service.get_session.return_value = None
        
        with pytest.raises(SessionNotFoundError):
            chat_service.send_message("non-existent-session", "Hello")
    
    def test_send_message_llm_failure(self, chat_service, mock_llm_service):
        """Test handling LLM generation failure"""
        mock_llm_service.generate_chat_response.return_value = Mock(
            success=False,
            error_message="Model not available"
        )
        
        with pytest.raises(ModelNotAvailableError):
            chat_service.send_message("test-session", "Hello")
    
    def test_build_context(self, chat_service, mock_history_service):
        """Test building conversation context"""
        # Mock message history
        mock_messages = [
            Message(
                id="msg1",
                session_id="test-session",
                role="user",
                content="Hello",
                timestamp=datetime.utcnow()
            ),
            Message(
                id="msg2",
                session_id="test-session",
                role="assistant",
                content="Hi there!",
                timestamp=datetime.utcnow()
            )
        ]
        mock_history_service.get_session_messages.return_value = mock_messages
        
        context = chat_service._build_context("test-session", limit=5)
        
        mock_history_service.get_session_messages.assert_called_once_with("test-session", limit=5)
        
        assert len(context) == 2
        assert context[0]["role"] == "user"
        assert context[0]["content"] == "Hello"
        assert context[1]["role"] == "assistant"
        assert context[1]["content"] == "Hi there!"
    
    def test_get_conversation_context(self, chat_service, mock_history_service):
        """Test getting conversation context"""
        mock_messages = [
            Message(
                id="msg1",
                session_id="test-session",
                role="user",
                content="Test message",
                timestamp=datetime.utcnow()
            )
        ]
        mock_history_service.get_session_messages.return_value = mock_messages
        
        result = chat_service.get_conversation_context("test-session", max_messages=10)
        
        mock_history_service.get_session_messages.assert_called_once_with("test-session", limit=10)
        assert result == mock_messages
    
    @pytest.mark.asyncio
    async def test_stream_message_success(self, chat_service, mock_llm_service, mock_session_service, mock_history_service):
        """Test streaming message functionality"""
        # Mock streaming response
        async def mock_stream():
            yield "Hello"
            yield " world"
            yield "!"
        
        mock_llm_service.stream_chat_response = AsyncMock(return_value=mock_stream())
        
        chunks = []
        async for chunk in chat_service.stream_message("test-session", "Hello"):
            chunks.append(chunk)
        
        # Verify chunks received
        assert chunks == ["Hello", " world", "!"]
        
        # Verify session was retrieved
        mock_session_service.get_session.assert_called_once_with("test-session")
        
        # Verify messages were saved
        assert mock_history_service.save_message.call_count == 2  # User + AI message
    
    @pytest.mark.asyncio
    async def test_stream_message_fallback(self, chat_service, mock_llm_service, mock_session_service, mock_history_service):
        """Test streaming fallback to regular response"""
        # LLM service doesn't support streaming
        delattr(mock_llm_service, 'stream_chat_response')
        
        chunks = []
        async for chunk in chat_service.stream_message("test-session", "Hello"):
            chunks.append(chunk)
        
        # Should receive full response as single chunk
        assert chunks == ["Test response"]
        
        # Verify regular generate was called
        mock_llm_service.generate_chat_response.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stream_message_session_not_found(self, chat_service, mock_session_service):
        """Test streaming to non-existent session"""
        mock_session_service.get_session.return_value = None
        
        with pytest.raises(SessionNotFoundError):
            async for chunk in chat_service.stream_message("non-existent-session", "Hello"):
                pass