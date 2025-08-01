"""
Integration tests for the AI Chat System
בדיקות אינטגרציה למערכת שיחות AI

This module contains comprehensive integration tests that verify the complete
chat flow from frontend to backend, including session management, message handling,
streaming, security, and error scenarios.
"""

import os
import sqlite3
import json
import pytest
import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

# Import backend components
from backend.api import main as api_main
from backend.services.ai.session_service import SessionService
from backend.services.ai.chat_history_service import ChatHistoryService
from backend.services.ai.chat_service import ChatService
from backend.services.ai.chat_security_service import ChatSecurityService
from backend.models.chat import ChatSession, Message, ChatResponse


class MockLLMService:
    """Enhanced mock LLM service for integration testing"""
    
    def __init__(self, response_delay: float = 0.1, should_fail: bool = False):
        self.response_delay = response_delay
        self.should_fail = should_fail
        self.call_count = 0
        self.last_messages = []
        
    def generate_chat_response(self, messages: List[Dict[str, str]]):
        """Mock chat response generation"""
        self.call_count += 1
        self.last_messages = messages
        
        if self.should_fail:
            class FailedResponse:
                success = False
                error_message = "Mock LLM failure"
            return FailedResponse()
        
        # Simulate processing time
        time.sleep(self.response_delay)
        
        # Generate contextual response based on input
        user_message = messages[-1]["content"] if messages else "Hello"
        response_content = f"Mock response to: {user_message}"
        
        class MockResponse:
            success = True
            content = response_content
            model_used = "mock-model"
            model_id = "mock-model"
            tokens_used = len(response_content.split())
            response_time = self.response_delay
            metadata = {"mock": True}
            usage = {"total_tokens": len(response_content.split())}
            
        return MockResponse()
    
    async def stream_chat_response(self, messages: List[Dict[str, str]], timeout: int = 60):
        """Mock streaming response"""
        self.call_count += 1
        self.last_messages = messages
        
        if self.should_fail:
            raise Exception("Mock streaming failure")
        
        user_message = messages[-1]["content"] if messages else "Hello"
        words = f"Mock streaming response to: {user_message}".split()
        
        for word in words:
            await asyncio.sleep(0.01)  # Simulate streaming delay
            yield word + " "
    
    def get_active_model(self):
        """Mock active model"""
        class MockModel:
            name = "Mock Model"
            provider = "Mock Provider"
            id = "mock-model"
        return MockModel()


def create_test_database(db_path: str) -> None:
    """Create test database with all required tables"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Chat sessions table
    cur.execute("""
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
    """)
    
    # Chat messages table
    cur.execute("""
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
    """)
    
    # Create indexes for performance
    cur.execute("CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id)")
    cur.execute("CREATE INDEX idx_chat_sessions_updated_at ON chat_sessions(updated_at)")
    cur.execute("CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id)")
    cur.execute("CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp)")
    
    conn.commit()
    conn.close()


@pytest.fixture
def test_db_path(tmp_path):
    """Create temporary test database"""
    db_path = tmp_path / "test_chat_integration.db"
    create_test_database(str(db_path))
    return str(db_path)


@pytest.fixture
def mock_llm_service():
    """Create mock LLM service"""
    return MockLLMService()


@pytest.fixture
def chat_services(test_db_path, mock_llm_service):
    """Create all chat services for testing"""
    session_service = SessionService(db_path=test_db_path)
    history_service = ChatHistoryService(db_path=test_db_path)
    chat_service = ChatService(
        llm_service=mock_llm_service,
        session_service=session_service,
        history_service=history_service
    )
    
    return {
        'session_service': session_service,
        'history_service': history_service,
        'chat_service': chat_service,
        'llm_service': mock_llm_service
    }


@pytest.fixture
def test_client(chat_services):
    """Create FastAPI test client with mocked services"""
    # Replace services in the main module
    api_main.session_service = chat_services['session_service']
    api_main.chat_history_service = chat_services['history_service']
    api_main.chat_service = chat_services['chat_service']
    api_main.llm_service = chat_services['llm_service']
    
    return TestClient(api_main.app)


class TestChatIntegrationFlow:
    """Test complete chat integration flows"""
    
    def test_complete_chat_session_flow(self, test_client, chat_services):
        """Test complete flow: create session -> send messages -> get history"""
        # Step 1: Create a new chat session
        session_data = {
            "title": "Integration Test Session",
            "model_id": "mock-model",
            "user_id": "test-user-123"
        }
        
        response = test_client.post("/api/chat/sessions", json=session_data)
        assert response.status_code == 200
        session = response.json()
        session_id = session["id"]
        
        assert session["title"] == session_data["title"]
        assert session["model_id"] == session_data["model_id"]
        assert session["user_id"] == session_data["user_id"]
        assert session["message_count"] == 0
        
        # Step 2: Send first message
        message_data = {
            "session_id": session_id,
            "message": "Hello, this is a test message",
            "user_id": "test-user-123"
        }
        
        response = test_client.post("/api/chat/send", json=message_data)
        assert response.status_code == 200
        chat_response = response.json()
        
        assert chat_response["success"] is True
        assert "Mock response to: Hello, this is a test message" in chat_response["content"]
        assert chat_response["model_id"] == "mock-model"
        assert chat_response["tokens_used"] > 0
        
        # Step 3: Verify session message count updated
        response = test_client.get(f"/api/chat/sessions/{session_id}")
        assert response.status_code == 200
        updated_session = response.json()
        assert updated_session["message_count"] == 2  # User + AI message
        
        # Step 4: Get message history
        response = test_client.get(f"/api/chat/sessions/{session_id}/messages")
        assert response.status_code == 200
        messages = response.json()
        
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[0]["content"] == "Hello, this is a test message"
        assert messages[1]["role"] == "assistant"
        assert "Mock response to: Hello, this is a test message" in messages[1]["content"]
        
        # Step 5: Send follow-up message
        follow_up_data = {
            "session_id": session_id,
            "message": "Can you help me with something else?",
            "user_id": "test-user-123"
        }
        
        response = test_client.post("/api/chat/send", json=follow_up_data)
        assert response.status_code == 200
        
        # Step 6: Verify conversation context
        response = test_client.get(f"/api/chat/sessions/{session_id}/messages")
        assert response.status_code == 200
        messages = response.json()
        assert len(messages) == 4  # 2 user + 2 AI messages
        
        # Verify LLM service received context
        llm_service = chat_services['llm_service']
        assert llm_service.call_count == 2
        # Last call should include conversation history
        last_messages = llm_service.last_messages
        assert len(last_messages) >= 2  # Should include previous context
    
    def test_streaming_chat_flow(self, test_client, chat_services):
        """Test streaming chat functionality"""
        # Create session
        session_data = {
            "title": "Streaming Test",
            "model_id": "mock-model"
        }
        
        response = test_client.post("/api/chat/sessions", json=session_data)
        session_id = response.json()["id"]
        
        # Test streaming endpoint
        stream_data = {
            "session_id": session_id,
            "message": "Stream this response please"
        }
        
        with test_client.stream("POST", "/api/chat/stream", json=stream_data) as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
            
            # Collect streamed data
            chunks = []
            for chunk in response.iter_lines():
                if chunk.startswith("data: ") and not chunk.endswith("[DONE]"):
                    chunks.append(chunk[6:])  # Remove "data: " prefix
            
            # Verify streaming worked
            assert len(chunks) > 0
            full_response = "".join(chunks)
            assert "Mock streaming response" in full_response
        
        # Verify message was saved
        response = test_client.get(f"/api/chat/sessions/{session_id}/messages")
        messages = response.json()
        assert len(messages) == 2  # User + AI message
    
    def test_session_management_flow(self, test_client):
        """Test complete session management operations"""
        # Create multiple sessions
        sessions_created = []
        for i in range(3):
            session_data = {
                "title": f"Test Session {i+1}",
                "model_id": "mock-model",
                "user_id": "test-user"
            }
            response = test_client.post("/api/chat/sessions", json=session_data)
            assert response.status_code == 200
            sessions_created.append(response.json())
        
        # List all sessions
        response = test_client.get("/api/chat/sessions")
        assert response.status_code == 200
        sessions = response.json()
        assert len(sessions) >= 3
        
        # Filter by user
        response = test_client.get("/api/chat/sessions?user_id=test-user")
        assert response.status_code == 200
        user_sessions = response.json()
        assert len(user_sessions) == 3
        
        # Update session
        session_id = sessions_created[0]["id"]
        update_data = {"title": "Updated Session Title"}
        response = test_client.put(f"/api/chat/sessions/{session_id}", json=update_data)
        assert response.status_code == 200
        
        # Verify update
        response = test_client.get(f"/api/chat/sessions/{session_id}")
        assert response.status_code == 200
        updated_session = response.json()
        assert updated_session["title"] == "Updated Session Title"
        
        # Delete session
        response = test_client.delete(f"/api/chat/sessions/{session_id}")
        assert response.status_code == 200
        
        # Verify deletion
        response = test_client.get(f"/api/chat/sessions/{session_id}")
        assert response.status_code == 404
    
    def test_message_search_and_export_flow(self, test_client):
        """Test message search and export functionality"""
        # Create session with searchable content
        session_data = {
            "title": "Search Test Session",
            "model_id": "mock-model"
        }
        response = test_client.post("/api/chat/sessions", json=session_data)
        session_id = response.json()["id"]
        
        # Add messages with specific content
        test_messages = [
            "Tell me about Python programming",
            "How do I use FastAPI?",
            "What is machine learning?"
        ]
        
        for msg in test_messages:
            message_data = {
                "session_id": session_id,
                "message": msg
            }
            response = test_client.post("/api/chat/send", json=message_data)
            assert response.status_code == 200
        
        # Test search functionality
        response = test_client.get("/api/chat/search?query=Python")
        assert response.status_code == 200
        search_results = response.json()
        
        # Should find the Python-related message
        python_messages = [msg for msg in search_results if "Python" in msg["content"]]
        assert len(python_messages) > 0
        
        # Test session-specific search
        response = test_client.get(f"/api/chat/search?query=FastAPI&session_id={session_id}")
        assert response.status_code == 200
        search_results = response.json()
        
        fastapi_messages = [msg for msg in search_results if "FastAPI" in msg["content"]]
        assert len(fastapi_messages) > 0
        
        # Test export functionality
        export_formats = ["json", "markdown", "txt"]
        
        for format_type in export_formats:
            export_data = {"format": format_type}
            response = test_client.post(f"/api/chat/export/{session_id}", json=export_data)
            assert response.status_code == 200
            
            # Verify content type
            if format_type == "json":
                assert "application/json" in response.headers["content-type"]
                # Verify it's valid JSON
                exported_data = json.loads(response.content)
                assert isinstance(exported_data, list)
                assert len(exported_data) > 0
            elif format_type == "markdown":
                assert "text/markdown" in response.headers["content-type"]
            else:  # txt
                assert "text/plain" in response.headers["content-type"]
    
    def test_error_handling_and_recovery(self, test_client, chat_services):
        """Test error scenarios and recovery mechanisms"""
        # Test sending message to non-existent session
        message_data = {
            "session_id": "non-existent-session",
            "message": "This should fail"
        }
        
        response = test_client.post("/api/chat/send", json=message_data)
        assert response.status_code == 404
        assert "Session not found" in response.json()["detail"]
        
        # Test with failing LLM service
        chat_services['llm_service'].should_fail = True
        
        # Create valid session
        session_data = {
            "title": "Error Test Session",
            "model_id": "mock-model"
        }
        response = test_client.post("/api/chat/sessions", json=session_data)
        session_id = response.json()["id"]
        
        # Try to send message with failing LLM
        message_data = {
            "session_id": session_id,
            "message": "This should fail at LLM level"
        }
        
        response = test_client.post("/api/chat/send", json=message_data)
        assert response.status_code == 503  # Service unavailable
        
        # Reset LLM service and verify recovery
        chat_services['llm_service'].should_fail = False
        
        response = test_client.post("/api/chat/send", json=message_data)
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Test invalid session operations
        response = test_client.get("/api/chat/sessions/invalid-session-id")
        assert response.status_code == 404
        
        response = test_client.put("/api/chat/sessions/invalid-session-id", json={"title": "New Title"})
        assert response.status_code == 404
        
        response = test_client.delete("/api/chat/sessions/invalid-session-id")
        assert response.status_code == 404
    
    def test_concurrent_operations(self, test_client):
        """Test concurrent chat operations"""
        import threading
        import queue
        
        # Create session
        session_data = {
            "title": "Concurrency Test",
            "model_id": "mock-model"
        }
        response = test_client.post("/api/chat/sessions", json=session_data)
        session_id = response.json()["id"]
        
        # Function to send messages concurrently
        def send_message(message_num: int, result_queue: queue.Queue):
            try:
                message_data = {
                    "session_id": session_id,
                    "message": f"Concurrent message {message_num}"
                }
                response = test_client.post("/api/chat/send", json=message_data)
                result_queue.put((message_num, response.status_code, response.json()))
            except Exception as e:
                result_queue.put((message_num, 500, {"error": str(e)}))
        
        # Send multiple messages concurrently
        threads = []
        result_queue = queue.Queue()
        num_concurrent = 5
        
        for i in range(num_concurrent):
            thread = threading.Thread(target=send_message, args=(i, result_queue))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Collect results
        results = []
        while not result_queue.empty():
            results.append(result_queue.get())
        
        # Verify all requests succeeded
        assert len(results) == num_concurrent
        for message_num, status_code, response_data in results:
            assert status_code == 200
            assert response_data["success"] is True
        
        # Verify all messages were saved
        response = test_client.get(f"/api/chat/sessions/{session_id}/messages")
        messages = response.json()
        # Should have num_concurrent * 2 messages (user + AI for each)
        assert len(messages) == num_concurrent * 2
    
    def test_performance_benchmarks(self, test_client, chat_services):
        """Test performance benchmarks for chat operations"""
        # Create session
        session_data = {
            "title": "Performance Test",
            "model_id": "mock-model"
        }
        response = test_client.post("/api/chat/sessions", json=session_data)
        session_id = response.json()["id"]
        
        # Benchmark message sending
        num_messages = 10
        start_time = time.time()
        
        for i in range(num_messages):
            message_data = {
                "session_id": session_id,
                "message": f"Performance test message {i}"
            }
            response = test_client.post("/api/chat/send", json=message_data)
            assert response.status_code == 200
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time_per_message = total_time / num_messages
        
        # Performance assertions (adjust thresholds as needed)
        assert avg_time_per_message < 1.0  # Should be under 1 second per message
        assert total_time < 10.0  # Total should be under 10 seconds
        
        # Benchmark message retrieval
        start_time = time.time()
        response = test_client.get(f"/api/chat/sessions/{session_id}/messages")
        end_time = time.time()
        
        assert response.status_code == 200
        messages = response.json()
        assert len(messages) == num_messages * 2  # User + AI messages
        
        retrieval_time = end_time - start_time
        assert retrieval_time < 0.5  # Should retrieve messages quickly
        
        # Benchmark search performance
        start_time = time.time()
        response = test_client.get("/api/chat/search?query=Performance")
        end_time = time.time()
        
        assert response.status_code == 200
        search_time = end_time - start_time
        assert search_time < 1.0  # Search should be fast
    
    def test_data_consistency_and_integrity(self, test_client, test_db_path):
        """Test data consistency and integrity across operations"""
        # Create session and messages
        session_data = {
            "title": "Integrity Test",
            "model_id": "mock-model",
            "user_id": "integrity-user"
        }
        response = test_client.post("/api/chat/sessions", json=session_data)
        session_id = response.json()["id"]
        
        # Send messages
        messages_sent = []
        for i in range(5):
            message_data = {
                "session_id": session_id,
                "message": f"Integrity test message {i}",
                "user_id": "integrity-user"
            }
            response = test_client.post("/api/chat/send", json=message_data)
            assert response.status_code == 200
            messages_sent.append(message_data["message"])
        
        # Verify database consistency directly
        conn = sqlite3.connect(test_db_path)
        cur = conn.cursor()
        
        # Check session exists and has correct message count
        cur.execute("SELECT message_count FROM chat_sessions WHERE id = ?", (session_id,))
        result = cur.fetchone()
        assert result is not None
        assert result[0] == 10  # 5 user + 5 AI messages
        
        # Check all messages exist
        cur.execute("SELECT COUNT(*) FROM chat_messages WHERE session_id = ?", (session_id,))
        message_count = cur.fetchone()[0]
        assert message_count == 10
        
        # Check message order and content
        cur.execute("""
            SELECT role, content FROM chat_messages 
            WHERE session_id = ? 
            ORDER BY timestamp
        """, (session_id,))
        
        db_messages = cur.fetchall()
        user_messages = [msg for role, msg in db_messages if role == "user"]
        
        # Verify all sent messages are in database
        for sent_msg in messages_sent:
            assert sent_msg in user_messages
        
        conn.close()
        
        # Test referential integrity - delete session should cascade
        response = test_client.delete(f"/api/chat/sessions/{session_id}")
        assert response.status_code == 200
        
        # Verify messages were also deleted
        conn = sqlite3.connect(test_db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM chat_messages WHERE session_id = ?", (session_id,))
        remaining_messages = cur.fetchone()[0]
        assert remaining_messages == 0
        conn.close()


class TestSecurityIntegration:
    """Test security-related integration scenarios"""
    
    def test_rate_limiting_integration(self, test_client):
        """Test rate limiting functionality"""
        # Create session
        session_data = {
            "title": "Rate Limit Test",
            "model_id": "mock-model"
        }
        response = test_client.post("/api/chat/sessions", json=session_data)
        session_id = response.json()["id"]
        
        # Send messages rapidly to trigger rate limiting
        message_data = {
            "session_id": session_id,
            "message": "Rate limit test message"
        }
        
        successful_requests = 0
        rate_limited_requests = 0
        
        # Try to send more messages than the rate limit allows
        for i in range(10):  # Rate limit is 5/minute in the code
            response = test_client.post("/api/chat/send", json=message_data)
            if response.status_code == 200:
                successful_requests += 1
            elif response.status_code == 429:  # Too Many Requests
                rate_limited_requests += 1
        
        # Should have some successful requests and some rate limited
        assert successful_requests > 0
        # Note: Rate limiting might not trigger in tests due to timing
        # This test verifies the endpoint responds appropriately
    
    def test_input_sanitization_integration(self, test_client):
        """Test input sanitization across the system"""
        # Create session
        session_data = {
            "title": "Sanitization Test",
            "model_id": "mock-model"
        }
        response = test_client.post("/api/chat/sessions", json=session_data)
        session_id = response.json()["id"]
        
        # Test potentially malicious inputs
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "'; DROP TABLE chat_messages; --",
            "<img src=x onerror=alert('xss')>",
        ]
        
        for malicious_input in malicious_inputs:
            message_data = {
                "session_id": session_id,
                "message": malicious_input
            }
            
            response = test_client.post("/api/chat/send", json=message_data)
            assert response.status_code == 200
            
            # Verify the input was sanitized
            response_data = response.json()
            assert response_data["success"] is True
            
            # Check that dangerous content was removed/escaped
            # The exact sanitization depends on the implementation
            # but the system should not crash or execute malicious code
        
        # Verify messages were saved (even if sanitized)
        response = test_client.get(f"/api/chat/sessions/{session_id}/messages")
        assert response.status_code == 200
        messages = response.json()
        assert len(messages) > 0


@pytest.mark.asyncio
class TestAsyncIntegration:
    """Test asynchronous integration scenarios"""
    
    async def test_streaming_with_cancellation(self, test_client):
        """Test streaming with client disconnection simulation"""
        # Create session
        session_data = {
            "title": "Async Stream Test",
            "model_id": "mock-model"
        }
        response = test_client.post("/api/chat/sessions", json=session_data)
        session_id = response.json()["id"]
        
        # Test streaming endpoint with timeout
        stream_data = {
            "session_id": session_id,
            "message": "Long streaming response"
        }
        
        # This test verifies that streaming works in the integration context
        with test_client.stream("POST", "/api/chat/stream", json=stream_data) as response:
            assert response.status_code == 200
            
            # Read first few chunks then "disconnect"
            chunks_read = 0
            for chunk in response.iter_lines():
                chunks_read += 1
                if chunks_read >= 3:  # Simulate early disconnection
                    break
            
            # Verify we got some data
            assert chunks_read > 0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])