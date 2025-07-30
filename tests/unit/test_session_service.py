"""
Unit tests for SessionService
"""
import pytest
import tempfile
import os
from datetime import datetime, timedelta

from backend.services.ai.session_service import SessionService
from backend.models.chat import ChatSession


class TestSessionService:
    """Test SessionService functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        fd, path = tempfile.mkstemp(suffix='.db')
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.fixture
    def session_service(self, temp_db):
        """Create SessionService instance with temporary database"""
        service = SessionService(db_path=temp_db)
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
    
    def test_create_session(self, session_service):
        """Test creating a new session"""
        session = session_service.create_session(
            title="Test Session",
            model_id="test-model",
            user_id="test-user"
        )
        
        assert session.title == "Test Session"
        assert session.model_id == "test-model"
        assert session.user_id == "test-user"
        assert session.message_count == 0
        assert not session.is_archived
        assert isinstance(session.id, str)
        assert len(session.id) > 0
    
    def test_create_session_with_defaults(self, session_service):
        """Test creating session with default values"""
        session = session_service.create_session()
        
        assert session.title == "New Chat"
        assert session.model_id == "default"
        assert session.user_id is None
        assert session.message_count == 0
    
    def test_get_session(self, session_service):
        """Test retrieving a session"""
        # Create a session first
        created_session = session_service.create_session(title="Test Session")
        
        # Retrieve it
        retrieved_session = session_service.get_session(created_session.id)
        
        assert retrieved_session is not None
        assert retrieved_session.id == created_session.id
        assert retrieved_session.title == "Test Session"
    
    def test_get_nonexistent_session(self, session_service):
        """Test retrieving non-existent session"""
        result = session_service.get_session("non-existent-id")
        assert result is None
    
    def test_list_user_sessions(self, session_service):
        """Test listing user sessions"""
        # Create sessions for different users
        session1 = session_service.create_session(title="User1 Session", user_id="user1")
        session2 = session_service.create_session(title="User2 Session", user_id="user2")
        session3 = session_service.create_session(title="User1 Session 2", user_id="user1")
        
        # List sessions for user1
        user1_sessions = session_service.list_user_sessions(user_id="user1")
        
        assert len(user1_sessions) == 2
        session_titles = [s.title for s in user1_sessions]
        assert "User1 Session" in session_titles
        assert "User1 Session 2" in session_titles
        assert "User2 Session" not in session_titles
    
    def test_list_all_sessions(self, session_service):
        """Test listing all sessions"""
        # Create sessions
        session1 = session_service.create_session(title="Session 1")
        session2 = session_service.create_session(title="Session 2")
        
        # List all sessions
        all_sessions = session_service.list_user_sessions()
        
        assert len(all_sessions) >= 2
        session_titles = [s.title for s in all_sessions]
        assert "Session 1" in session_titles
        assert "Session 2" in session_titles
    
    def test_update_session(self, session_service):
        """Test updating session"""
        session = session_service.create_session(title="Original Title")
        
        # Update the session
        success = session_service.update_session(
            session.id,
            title="Updated Title",
            metadata={"key": "value"}
        )
        
        assert success is True
        
        # Verify the update
        updated_session = session_service.get_session(session.id)
        assert updated_session.title == "Updated Title"
        assert updated_session.metadata == {"key": "value"}
    
    def test_update_nonexistent_session(self, session_service):
        """Test updating non-existent session"""
        success = session_service.update_session("non-existent-id", title="New Title")
        assert success is False
    
    def test_delete_session(self, session_service):
        """Test deleting session"""
        session = session_service.create_session(title="To Delete")
        
        # Delete the session
        success = session_service.delete_session(session.id)
        assert success is True
        
        # Verify it's deleted
        deleted_session = session_service.get_session(session.id)
        assert deleted_session is None
    
    def test_delete_nonexistent_session(self, session_service):
        """Test deleting non-existent session"""
        success = session_service.delete_session("non-existent-id")
        assert success is False
    
    def test_increment_message_count(self, session_service):
        """Test incrementing message count"""
        session = session_service.create_session()
        original_count = session.message_count
        
        # Increment by 1
        session_service.increment_message_count(session.id, 1)
        
        # Verify increment
        updated_session = session_service.get_session(session.id)
        assert updated_session.message_count == original_count + 1
        
        # Increment by 5
        session_service.increment_message_count(session.id, 5)
        
        # Verify increment
        updated_session = session_service.get_session(session.id)
        assert updated_session.message_count == original_count + 6
    
    def test_archive_session(self, session_service):
        """Test archiving session"""
        session = session_service.create_session()
        assert not session.is_archived
        
        # Archive the session
        success = session_service.archive_session(session.id)
        assert success is True
        
        # Verify it's archived
        archived_session = session_service.get_session(session.id)
        assert archived_session.is_archived is True
    
    def test_unarchive_session(self, session_service):
        """Test unarchiving session"""
        session = session_service.create_session()
        
        # Archive first
        session_service.archive_session(session.id)
        
        # Then unarchive
        success = session_service.unarchive_session(session.id)
        assert success is True
        
        # Verify it's unarchived
        unarchived_session = session_service.get_session(session.id)
        assert unarchived_session.is_archived is False
    
    def test_search_sessions(self, session_service):
        """Test searching sessions"""
        # Create sessions with different titles
        session1 = session_service.create_session(title="Python Programming")
        session2 = session_service.create_session(title="JavaScript Tutorial")
        session3 = session_service.create_session(title="Python Data Science")
        
        # Search for Python sessions
        python_sessions = session_service.search_sessions("Python")
        
        assert len(python_sessions) == 2
        titles = [s.title for s in python_sessions]
        assert "Python Programming" in titles
        assert "Python Data Science" in titles
        assert "JavaScript Tutorial" not in titles
    
    def test_get_session_stats(self, session_service):
        """Test getting session statistics"""
        session = session_service.create_session(title="Stats Test")
        
        # Get stats for empty session
        stats = session_service.get_session_stats(session.id)
        
        assert stats is not None
        assert stats["session_id"] == session.id
        assert stats["title"] == "Stats Test"
        assert stats["message_count"] == 0
        assert stats["total_tokens"] == 0
        assert stats["avg_response_time"] == 0
    
    def test_get_stats_nonexistent_session(self, session_service):
        """Test getting stats for non-existent session"""
        stats = session_service.get_session_stats("non-existent-id")
        assert stats is None
    
    def test_cleanup_old_sessions_dry_run(self, session_service):
        """Test cleanup old sessions in dry run mode"""
        # Create an old archived session
        session = session_service.create_session(title="Old Session")
        session_service.archive_session(session.id)
        
        # Run cleanup in dry run mode
        count = session_service.cleanup_old_sessions(days_old=0, dry_run=True)
        
        # Should find the session but not delete it
        assert count >= 1
        
        # Verify session still exists
        existing_session = session_service.get_session(session.id)
        assert existing_session is not None
    
    def test_cleanup_old_sessions_actual(self, session_service):
        """Test actual cleanup of old sessions"""
        # Create an old archived session
        session = session_service.create_session(title="Old Session")
        session_service.archive_session(session.id)
        
        # Run actual cleanup
        count = session_service.cleanup_old_sessions(days_old=0, dry_run=False)
        
        # Should find and delete the session
        assert count >= 1
        
        # Verify session is deleted
        deleted_session = session_service.get_session(session.id)
        assert deleted_session is None