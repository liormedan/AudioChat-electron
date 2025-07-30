"""
Unit tests for ChatHistoryService
"""
import pytest
import tempfile
import os
import json
from datetime import datetime

from backend.services.ai.chat_history_service import ChatHistoryService
from backend.models.chat import Message


class TestChatHistoryService:
    """Test ChatHistoryService functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.fixture
    def history_service(self, temp_db):
        """Create ChatHistoryService instance with temporary database"""
        service = ChatHistoryService(db_path=temp_db)
        # Initialize the database tables manually for testing
        import sqlite3
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute('''
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
        ''')
        cursor.execute('''
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
        ''')
        conn.commit()
        conn.close()
        return service
    
    @pytest.fixture
    def sample_message(self):
        """Create a sample message for testing"""
        return Message(
            id="test-msg-1",
            session_id="test-session-1",
            role="user",
            content="Hello, world!",
            timestamp=datetime.utcnow(),
            model_id="test-model",
            tokens_used=5,
            response_time=1.2,
            metadata={"test": True}
        )
    
    def test_save_message(self, history_service, sample_message):
        """Test saving a message"""
        message_id = history_service.save_message("test-session-1", sample_message)
        
        assert message_id == sample_message.id
        
        # Verify message was saved
        saved_message = history_service.get_message_by_id(message_id)
        assert saved_message is not None
        assert saved_message.content == "Hello, world!"
        assert saved_message.role == "user"
        assert saved_message.session_id == "test-session-1"
    
    def test_save_message_without_id(self, history_service):
        """Test saving message without ID (should generate one)"""
        message = Message(
            id="",  # Empty ID
            session_id="test-session-1",
            role="user",
            content="Test message",
            timestamp=datetime.utcnow()
        )
        
        message_id = history_service.save_message("test-session-1", message)
        
        assert message_id != ""
        assert len(message_id) > 0
        
        # Verify message was saved with generated ID
        saved_message = history_service.get_message_by_id(message_id)
        assert saved_message is not None
        assert saved_message.content == "Test message"
    
    def test_get_session_messages(self, history_service):
        """Test retrieving session messages"""
        # Create test messages
        messages = [
            Message(
                id=f"msg-{i}",
                session_id="test-session-1",
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
                timestamp=datetime.utcnow()
            )
            for i in range(5)
        ]
        
        # Save messages
        for msg in messages:
            history_service.save_message("test-session-1", msg)
        
        # Retrieve messages
        retrieved_messages = history_service.get_session_messages("test-session-1")
        
        assert len(retrieved_messages) == 5
        assert retrieved_messages[0].content == "Message 0"
        assert retrieved_messages[4].content == "Message 4"
    
    def test_get_session_messages_with_limit(self, history_service):
        """Test retrieving session messages with limit"""
        # Create test messages
        for i in range(10):
            message = Message(
                id=f"msg-{i}",
                session_id="test-session-1",
                role="user",
                content=f"Message {i}",
                timestamp=datetime.utcnow()
            )
            history_service.save_message("test-session-1", message)
        
        # Retrieve with limit
        limited_messages = history_service.get_session_messages("test-session-1", limit=3)
        
        assert len(limited_messages) == 3
    
    def test_get_session_messages_with_offset(self, history_service):
        """Test retrieving session messages with offset"""
        # Create test messages
        for i in range(5):
            message = Message(
                id=f"msg-{i}",
                session_id="test-session-1",
                role="user",
                content=f"Message {i}",
                timestamp=datetime.utcnow()
            )
            history_service.save_message("test-session-1", message)
        
        # Retrieve with offset
        offset_messages = history_service.get_session_messages("test-session-1", limit=2, offset=2)
        
        assert len(offset_messages) == 2
        assert offset_messages[0].content == "Message 2"
        assert offset_messages[1].content == "Message 3"
    
    def test_search_messages(self, history_service):
        """Test searching messages"""
        # Create test messages with different content
        messages = [
            Message(id="msg-1", session_id="session-1", role="user", content="Python programming", timestamp=datetime.utcnow()),
            Message(id="msg-2", session_id="session-1", role="user", content="JavaScript tutorial", timestamp=datetime.utcnow()),
            Message(id="msg-3", session_id="session-2", role="user", content="Python data science", timestamp=datetime.utcnow()),
        ]
        
        # Create sessions first
        import sqlite3
        conn = sqlite3.connect(history_service.db_path)
        cursor = conn.cursor()
        for session_id in ["session-1", "session-2"]:
            cursor.execute(
                "INSERT INTO chat_sessions VALUES (?,?,?,?,?,?,?,?,?)",
                (session_id, "Test", "model", None, datetime.utcnow().isoformat(), 
                 datetime.utcnow().isoformat(), 0, 0, "{}")
            )
        conn.commit()
        conn.close()
        
        # Save messages
        for msg in messages:
            history_service.save_message(msg.session_id, msg)
        
        # Search for Python messages
        python_messages = history_service.search_messages("Python")
        
        assert len(python_messages) == 2
        contents = [m.content for m in python_messages]
        assert "Python programming" in contents
        assert "Python data science" in contents
        assert "JavaScript tutorial" not in contents
    
    def test_search_messages_by_session(self, history_service):
        """Test searching messages within specific session"""
        # Create sessions first
        import sqlite3
        conn = sqlite3.connect(history_service.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_sessions VALUES (?,?,?,?,?,?,?,?,?)",
            ("session-1", "Test", "model", None, datetime.utcnow().isoformat(), 
             datetime.utcnow().isoformat(), 0, 0, "{}")
        )
        conn.commit()
        conn.close()
        
        # Create test messages
        messages = [
            Message(id="msg-1", session_id="session-1", role="user", content="test message", timestamp=datetime.utcnow()),
            Message(id="msg-2", session_id="session-1", role="user", content="another test", timestamp=datetime.utcnow()),
        ]
        
        for msg in messages:
            history_service.save_message(msg.session_id, msg)
        
        # Search within specific session
        session_messages = history_service.search_messages("test", session_id="session-1")
        
        assert len(session_messages) == 2
    
    def test_export_session_json(self, history_service, sample_message):
        """Test exporting session as JSON"""
        history_service.save_message("test-session-1", sample_message)
        
        json_export = history_service.export_session("test-session-1", format="json")
        
        # Parse JSON to verify structure
        data = json.loads(json_export)
        assert len(data) == 1
        assert data[0]["content"] == "Hello, world!"
        assert data[0]["role"] == "user"
    
    def test_export_session_markdown(self, history_service, sample_message):
        """Test exporting session as Markdown"""
        history_service.save_message("test-session-1", sample_message)
        
        markdown_export = history_service.export_session("test-session-1", format="markdown")
        
        assert "# Chat Session Export" in markdown_export
        assert "👤 User" in markdown_export
        assert "Hello, world!" in markdown_export
        assert "Model: test-model" in markdown_export
    
    def test_export_session_text(self, history_service, sample_message):
        """Test exporting session as plain text"""
        history_service.save_message("test-session-1", sample_message)
        
        text_export = history_service.export_session("test-session-1", format="txt")
        
        assert "Chat Session Export" in text_export
        assert "USER: Hello, world!" in text_export
    
    def test_export_session_invalid_format(self, history_service):
        """Test exporting with invalid format"""
        with pytest.raises(ValueError, match="Unsupported export format"):
            history_service.export_session("test-session-1", format="invalid")
    
    def test_get_message_count(self, history_service):
        """Test getting message count for session"""
        # Initially should be 0
        count = history_service.get_message_count("test-session-1")
        assert count == 0
        
        # Add messages
        for i in range(3):
            message = Message(
                id=f"msg-{i}",
                session_id="test-session-1",
                role="user",
                content=f"Message {i}",
                timestamp=datetime.utcnow()
            )
            history_service.save_message("test-session-1", message)
        
        # Should now be 3
        count = history_service.get_message_count("test-session-1")
        assert count == 3
    
    def test_delete_message(self, history_service, sample_message):
        """Test deleting a specific message"""
        message_id = history_service.save_message("test-session-1", sample_message)
        
        # Verify message exists
        assert history_service.get_message_by_id(message_id) is not None
        
        # Delete message
        success = history_service.delete_message(message_id)
        assert success is True
        
        # Verify message is deleted
        assert history_service.get_message_by_id(message_id) is None
    
    def test_delete_nonexistent_message(self, history_service):
        """Test deleting non-existent message"""
        success = history_service.delete_message("non-existent-id")
        assert success is False
    
    def test_delete_session_messages(self, history_service):
        """Test deleting all messages for a session"""
        # Add messages
        for i in range(3):
            message = Message(
                id=f"msg-{i}",
                session_id="test-session-1",
                role="user",
                content=f"Message {i}",
                timestamp=datetime.utcnow()
            )
            history_service.save_message("test-session-1", message)
        
        # Verify messages exist
        assert history_service.get_message_count("test-session-1") == 3
        
        # Delete all messages
        count = history_service.delete_session_messages("test-session-1")
        assert count == 3
        
        # Verify messages are deleted
        assert history_service.get_message_count("test-session-1") == 0
    
    def test_update_message(self, history_service, sample_message):
        """Test updating a message"""
        message_id = history_service.save_message("test-session-1", sample_message)
        
        # Update message
        success = history_service.update_message(
            message_id,
            content="Updated content",
            metadata={"updated": True}
        )
        assert success is True
        
        # Verify update
        updated_message = history_service.get_message_by_id(message_id)
        assert updated_message.content == "Updated content"
        assert updated_message.metadata == {"updated": True}
    
    def test_get_session_statistics(self, history_service):
        """Test getting session statistics"""
        # Add various messages
        messages = [
            Message(id="msg-1", session_id="test-session-1", role="user", content="Hello", timestamp=datetime.utcnow(), tokens_used=5, response_time=1.0),
            Message(id="msg-2", session_id="test-session-1", role="assistant", content="Hi", timestamp=datetime.utcnow(), tokens_used=3, response_time=0.5),
            Message(id="msg-3", session_id="test-session-1", role="user", content="How are you?", timestamp=datetime.utcnow(), tokens_used=7, response_time=1.5),
        ]
        
        for msg in messages:
            history_service.save_message("test-session-1", msg)
        
        # Get statistics
        stats = history_service.get_session_statistics("test-session-1")
        
        assert stats["session_id"] == "test-session-1"
        assert stats["message_counts"]["total"] == 3
        assert stats["message_counts"]["user"] == 2
        assert stats["message_counts"]["assistant"] == 1
        assert stats["token_usage"]["total"] == 15
        assert stats["token_usage"]["average"] == 5.0
        assert stats["response_times"]["average"] == 1.0