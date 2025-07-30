"""
Unit tests for chat models
"""
import pytest
from datetime import datetime
from backend.models.chat import ChatSession, Message, ChatResponse, MessageRole, SessionStatus


class TestChatSession:
    """Test ChatSession model"""
    
    def test_create_chat_session(self):
        """Test creating a chat session"""
        now = datetime.utcnow()
        session = ChatSession(
            id="test-session-1",
            title="Test Session",
            model_id="test-model",
            user_id="test-user",
            created_at=now,
            updated_at=now,
            message_count=0
        )
        
        assert session.id == "test-session-1"
        assert session.title == "Test Session"
        assert session.model_id == "test-model"
        assert session.user_id == "test-user"
        assert session.message_count == 0
        assert not session.is_archived
        assert session.metadata == {}
    
    def test_session_to_dict(self):
        """Test converting session to dictionary"""
        now = datetime.utcnow()
        session = ChatSession(
            id="test-session-1",
            title="Test Session",
            model_id="test-model",
            user_id="test-user",
            created_at=now,
            updated_at=now,
            message_count=5,
            metadata={"key": "value"}
        )
        
        result = session.to_dict()
        
        assert result["id"] == "test-session-1"
        assert result["title"] == "Test Session"
        assert result["model_id"] == "test-model"
        assert result["user_id"] == "test-user"
        assert result["message_count"] == 5
        assert result["metadata"] == {"key": "value"}
        assert "created_at" in result
        assert "updated_at" in result
    
    def test_session_from_dict(self):
        """Test creating session from dictionary"""
        now = datetime.utcnow()
        data = {
            "id": "test-session-1",
            "title": "Test Session",
            "model_id": "test-model",
            "user_id": "test-user",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "message_count": 5,
            "is_archived": False,
            "metadata": {"key": "value"}
        }
        
        session = ChatSession.from_dict(data)
        
        assert session.id == "test-session-1"
        assert session.title == "Test Session"
        assert session.model_id == "test-model"
        assert session.user_id == "test-user"
        assert session.message_count == 5
        assert not session.is_archived
        assert session.metadata == {"key": "value"}


class TestMessage:
    """Test Message model"""
    
    def test_create_message(self):
        """Test creating a message"""
        now = datetime.utcnow()
        message = Message(
            id="test-msg-1",
            session_id="test-session-1",
            role=MessageRole.USER.value,
            content="Hello, world!",
            timestamp=now
        )
        
        assert message.id == "test-msg-1"
        assert message.session_id == "test-session-1"
        assert message.role == MessageRole.USER.value
        assert message.content == "Hello, world!"
        assert message.timestamp == now
        assert message.model_id is None
        assert message.tokens_used is None
        assert message.response_time is None
        assert message.metadata == {}
    
    def test_message_to_dict(self):
        """Test converting message to dictionary"""
        now = datetime.utcnow()
        message = Message(
            id="test-msg-1",
            session_id="test-session-1",
            role=MessageRole.ASSISTANT.value,
            content="Hello back!",
            timestamp=now,
            model_id="test-model",
            tokens_used=10,
            response_time=1.5,
            metadata={"confidence": 0.95}
        )
        
        result = message.to_dict()
        
        assert result["id"] == "test-msg-1"
        assert result["session_id"] == "test-session-1"
        assert result["role"] == MessageRole.ASSISTANT.value
        assert result["content"] == "Hello back!"
        assert result["model_id"] == "test-model"
        assert result["tokens_used"] == 10
        assert result["response_time"] == 1.5
        assert result["metadata"] == {"confidence": 0.95}
        assert "timestamp" in result
    
    def test_message_from_dict(self):
        """Test creating message from dictionary"""
        now = datetime.utcnow()
        data = {
            "id": "test-msg-1",
            "session_id": "test-session-1",
            "role": MessageRole.USER.value,
            "content": "Test message",
            "timestamp": now.isoformat(),
            "model_id": "test-model",
            "tokens_used": 5,
            "response_time": 0.8,
            "metadata": {"test": True}
        }
        
        message = Message.from_dict(data)
        
        assert message.id == "test-msg-1"
        assert message.session_id == "test-session-1"
        assert message.role == MessageRole.USER.value
        assert message.content == "Test message"
        assert message.model_id == "test-model"
        assert message.tokens_used == 5
        assert message.response_time == 0.8
        assert message.metadata == {"test": True}


class TestChatResponse:
    """Test ChatResponse model"""
    
    def test_create_chat_response(self):
        """Test creating a chat response"""
        response = ChatResponse(
            content="This is a response",
            model_id="test-model",
            tokens_used=15,
            response_time=2.1,
            success=True
        )
        
        assert response.content == "This is a response"
        assert response.model_id == "test-model"
        assert response.tokens_used == 15
        assert response.response_time == 2.1
        assert response.success is True
        assert response.error_message is None
        assert response.metadata == {}
    
    def test_chat_response_with_error(self):
        """Test creating a chat response with error"""
        response = ChatResponse(
            content="",
            model_id="test-model",
            tokens_used=0,
            response_time=0.5,
            success=False,
            error_message="Model not available"
        )
        
        assert response.content == ""
        assert response.success is False
        assert response.error_message == "Model not available"
    
    def test_chat_response_to_dict(self):
        """Test converting chat response to dictionary"""
        response = ChatResponse(
            content="Response content",
            model_id="test-model",
            tokens_used=20,
            response_time=1.8,
            success=True,
            metadata={"temperature": 0.7}
        )
        
        result = response.to_dict()
        
        assert result["content"] == "Response content"
        assert result["model_id"] == "test-model"
        assert result["tokens_used"] == 20
        assert result["response_time"] == 1.8
        assert result["success"] is True
        assert result["error_message"] is None
        assert result["metadata"] == {"temperature": 0.7}
    
    def test_chat_response_from_dict(self):
        """Test creating chat response from dictionary"""
        data = {
            "content": "Test response",
            "model_id": "test-model",
            "tokens_used": 12,
            "response_time": 1.2,
            "success": True,
            "error_message": None,
            "metadata": {"test": "value"}
        }
        
        response = ChatResponse.from_dict(data)
        
        assert response.content == "Test response"
        assert response.model_id == "test-model"
        assert response.tokens_used == 12
        assert response.response_time == 1.2
        assert response.success is True
        assert response.error_message is None
        assert response.metadata == {"test": "value"}


class TestMessageRole:
    """Test MessageRole enum"""
    
    def test_message_roles(self):
        """Test message role values"""
        assert MessageRole.USER.value == "user"
        assert MessageRole.ASSISTANT.value == "assistant"
        assert MessageRole.SYSTEM.value == "system"


class TestSessionStatus:
    """Test SessionStatus enum"""
    
    def test_session_statuses(self):
        """Test session status values"""
        assert SessionStatus.ACTIVE.value == "active"
        assert SessionStatus.ARCHIVED.value == "archived"
        assert SessionStatus.DELETED.value == "deleted"