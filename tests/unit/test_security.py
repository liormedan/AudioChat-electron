
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)

def test_rate_limiting():
    # Make more requests than the limit to trigger a 429 error
    for _ in range(6):
        response = client.post("/api/chat/send", json={"session_id": "test", "message": "test"})
        if response.status_code == 429:
            break
    assert response.status_code == 429

def test_input_sanitization():
    from backend.services.ai.chat_security_service import security_service
    sanitized_text = security_service.sanitize_input("<script>alert('xss')</script>")
    assert "<script>" not in sanitized_text
    assert "alert('xss')" in sanitized_text # a more robust test would check for the exact output
