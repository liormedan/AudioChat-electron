# Chat API Documentation

## Overview

The Chat API provides endpoints for managing AI conversations, sessions, and message history. It supports both synchronous and streaming responses, with built-in security features including rate limiting and input sanitization.

## Base URL

```
http://127.0.0.1:5000/api/chat
```

## Authentication

Currently, the API uses optional user_id parameters for user identification. Session access is validated based on user ownership.

## Rate Limiting

- Chat endpoints: 5 requests per minute per user
- Rate limits are enforced per IP address and user ID
- Rate limit headers are included in responses

## Error Handling

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error description",
  "error_type": "ErrorClassName"
}
```

Common HTTP status codes:
- `400` - Bad Request (invalid parameters)
- `403` - Forbidden (access denied)
- `404` - Not Found (session/message not found)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error
- `503` - Service Unavailable (LLM service down)

## Endpoints

### Send Message

Send a message to an AI model and receive a response.

**Endpoint:** `POST /api/chat/send`

**Request Body:**
```json
{
  "session_id": "string",
  "message": "string",
  "user_id": "string (optional)"
}
```

**Response:**
```json
{
  "content": "AI response text",
  "model_id": "local-gemma-3-4b-it",
  "tokens_used": 150,
  "response_time": 2.5,
  "success": true,
  "error_message": null,
  "metadata": {}
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/chat/send \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess_123",
    "message": "Hello, how are you?",
    "user_id": "user_456"
  }'
```

### Stream Message

Send a message and receive a streaming response using Server-Sent Events.

**Endpoint:** `POST /api/chat/stream`

**Request Body:**
```json
{
  "session_id": "string",
  "message": "string", 
  "user_id": "string (optional)"
}
```

**Response:** Server-Sent Events stream
```
data: {"chunk": "Hello", "type": "content"}

data: {"chunk": " there!", "type": "content"}

data: {"type": "done", "total_tokens": 150, "response_time": 2.5}

data: [DONE]
```

**Example:**
```javascript
const eventSource = new EventSource('/api/chat/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: 'sess_123',
    message: 'Tell me a story',
    user_id: 'user_456'
  })
});

eventSource.onmessage = (event) => {
  if (event.data === '[DONE]') {
    eventSource.close();
    return;
  }
  
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## Session Management

### List Sessions

Get a list of chat sessions for a user.

**Endpoint:** `GET /api/chat/sessions`

**Query Parameters:**
- `user_id` (optional): Filter sessions by user ID
- `limit` (optional): Maximum number of sessions to return (default: 50)
- `offset` (optional): Number of sessions to skip (default: 0)

**Response:**
```json
[
  {
    "id": "sess_123",
    "title": "General Chat",
    "model_id": "local-gemma-3-4b-it",
    "user_id": "user_456",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:45:00Z",
    "message_count": 12,
    "is_archived": false,
    "metadata": {}
  }
]
```

### Create Session

Create a new chat session.

**Endpoint:** `POST /api/chat/sessions`

**Request Body:**
```json
{
  "title": "string (optional)",
  "model_id": "string (optional)",
  "user_id": "string (optional)",
  "metadata": "object (optional)"
}
```

**Response:**
```json
{
  "id": "sess_789",
  "title": "New Chat",
  "model_id": "local-gemma-3-4b-it",
  "user_id": "user_456",
  "created_at": "2024-01-15T12:00:00Z",
  "updated_at": "2024-01-15T12:00:00Z",
  "message_count": 0,
  "is_archived": false,
  "metadata": {}
}
```

### Get Session

Get details of a specific session.

**Endpoint:** `GET /api/chat/sessions/{session_id}`

**Response:**
```json
{
  "id": "sess_123",
  "title": "General Chat",
  "model_id": "local-gemma-3-4b-it",
  "user_id": "user_456",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z",
  "message_count": 12,
  "is_archived": false,
  "metadata": {}
}
```

### Update Session

Update session properties.

**Endpoint:** `PUT /api/chat/sessions/{session_id}`

**Request Body:**
```json
{
  "title": "string (optional)",
  "is_archived": "boolean (optional)",
  "metadata": "object (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Session updated successfully"
}
```

### Delete Session

Delete a session and all its messages.

**Endpoint:** `DELETE /api/chat/sessions/{session_id}`

**Response:**
```json
{
  "success": true,
  "message": "Session deleted successfully"
}
```

## Message Management

### Get Session Messages

Retrieve messages for a specific session.

**Endpoint:** `GET /api/chat/sessions/{session_id}/messages`

**Query Parameters:**
- `limit` (optional): Maximum number of messages (default: 50)
- `offset` (optional): Number of messages to skip (default: 0)

**Response:**
```json
[
  {
    "id": "msg_123",
    "session_id": "sess_123",
    "role": "user",
    "content": "Hello!",
    "type": "text",
    "timestamp": "2024-01-15T10:30:00Z",
    "model_id": null,
    "tokens_used": null,
    "response_time": null,
    "metadata": {}
  },
  {
    "id": "msg_124",
    "session_id": "sess_123",
    "role": "assistant",
    "content": "Hello! How can I help you today?",
    "type": "text",
    "timestamp": "2024-01-15T10:30:05Z",
    "model_id": "local-gemma-3-4b-it",
    "tokens_used": 25,
    "response_time": 1.2,
    "metadata": {}
  }
]
```

### Add Message to Session

Add a message to a session (useful for importing or manual entry).

**Endpoint:** `POST /api/chat/sessions/{session_id}/messages`

**Request Body:**
```json
{
  "role": "user|assistant|system",
  "content": "string",
  "type": "text|audio|image|file (optional)",
  "model_id": "string (optional)",
  "tokens_used": "number (optional)",
  "response_time": "number (optional)",
  "metadata": "object (optional)"
}
```

**Response:**
```json
{
  "id": "msg_125",
  "session_id": "sess_123",
  "role": "user",
  "content": "Added message",
  "type": "text",
  "timestamp": "2024-01-15T12:00:00Z",
  "model_id": null,
  "tokens_used": null,
  "response_time": null,
  "metadata": {}
}
```

### Search Messages

Search for messages across sessions.

**Endpoint:** `GET /api/chat/search`

**Query Parameters:**
- `query` (required): Search query string
- `user_id` (optional): Filter by user ID
- `session_id` (optional): Filter by session ID
- `limit` (optional): Maximum results (default: 50)

**Response:**
```json
[
  {
    "id": "msg_123",
    "session_id": "sess_123",
    "role": "user",
    "content": "Hello world!",
    "type": "text",
    "timestamp": "2024-01-15T10:30:00Z",
    "model_id": null,
    "tokens_used": null,
    "response_time": null,
    "metadata": {},
    "session_title": "General Chat"
  }
]
```

### Export Session

Export session messages in various formats.

**Endpoint:** `POST /api/chat/export/{session_id}`

**Request Body:**
```json
{
  "format": "json|markdown|csv",
  "include_metadata": "boolean (optional)",
  "date_range": {
    "start": "2024-01-01T00:00:00Z (optional)",
    "end": "2024-01-31T23:59:59Z (optional)"
  }
}
```

**Response:**
```json
{
  "success": true,
  "format": "json",
  "data": "exported content as string",
  "filename": "chat_session_sess_123_2024-01-15.json",
  "size": 1024
}
```

## Model Management

### Get Available Models

**Endpoint:** `GET /api/llm/models`

**Response:**
```json
[
  {
    "id": "local-gemma-3-4b-it",
    "name": "Gemma 3 4B Instruct",
    "provider": "Local Gemma",
    "is_available": true,
    "parameters": {
      "max_tokens": 4096,
      "temperature": 0.7,
      "top_p": 0.9
    }
  }
]
```

### Get Active Model

**Endpoint:** `GET /api/llm/active-model`

**Response:**
```json
{
  "id": "local-gemma-3-4b-it",
  "name": "Gemma 3 4B Instruct", 
  "provider": "Local Gemma",
  "is_available": true,
  "parameters": {
    "max_tokens": 4096,
    "temperature": 0.7,
    "top_p": 0.9
  }
}
```

### Set Active Model

**Endpoint:** `POST /api/llm/active-model`

**Request Body:**
```json
{
  "model_id": "local-gemma-3-4b-it"
}
```

**Response:**
```json
{
  "success": true
}
```

## WebSocket Support (Future)

The API is designed to support WebSocket connections for real-time chat features:

```javascript
const ws = new WebSocket('ws://127.0.0.1:5000/ws/chat');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'join_session',
    session_id: 'sess_123',
    user_id: 'user_456'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

## SDK Examples

### Python SDK Example

```python
import requests
import json

class ChatAPI:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
    
    def send_message(self, session_id, message, user_id=None):
        response = requests.post(
            f"{self.base_url}/api/chat/send",
            json={
                "session_id": session_id,
                "message": message,
                "user_id": user_id
            }
        )
        return response.json()
    
    def create_session(self, title=None, user_id=None):
        response = requests.post(
            f"{self.base_url}/api/chat/sessions",
            json={
                "title": title,
                "user_id": user_id
            }
        )
        return response.json()

# Usage
api = ChatAPI()
session = api.create_session("My Chat", "user_123")
response = api.send_message(session["id"], "Hello!", "user_123")
print(response["content"])
```

### JavaScript SDK Example

```javascript
class ChatAPI {
  constructor(baseUrl = 'http://127.0.0.1:5000') {
    this.baseUrl = baseUrl;
  }

  async sendMessage(sessionId, message, userId = null) {
    const response = await fetch(`${this.baseUrl}/api/chat/send`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
        user_id: userId
      })
    });
    return response.json();
  }

  async createSession(title = null, userId = null) {
    const response = await fetch(`${this.baseUrl}/api/chat/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: title,
        user_id: userId
      })
    });
    return response.json();
  }

  async streamMessage(sessionId, message, userId = null) {
    const response = await fetch(`${this.baseUrl}/api/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
        user_id: userId
      })
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') return;
          
          try {
            const parsed = JSON.parse(data);
            console.log('Received:', parsed);
          } catch (e) {
            // Handle parsing errors
          }
        }
      }
    }
  }
}

// Usage
const api = new ChatAPI();
const session = await api.createSession('My Chat', 'user_123');
const response = await api.sendMessage(session.id, 'Hello!', 'user_123');
console.log(response.content);
```

## Testing

### Unit Tests

```bash
# Test individual endpoints
curl -X GET http://127.0.0.1:5000/api/chat/sessions
curl -X POST http://127.0.0.1:5000/api/chat/sessions \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Session"}'
```

### Integration Tests

```python
import pytest
from backend.api.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_create_and_send_message():
    # Create session
    session_response = client.post("/api/chat/sessions", json={
        "title": "Test Session",
        "user_id": "test_user"
    })
    assert session_response.status_code == 200
    session = session_response.json()
    
    # Send message
    message_response = client.post("/api/chat/send", json={
        "session_id": session["id"],
        "message": "Hello test",
        "user_id": "test_user"
    })
    assert message_response.status_code == 200
    response = message_response.json()
    assert response["success"] == True
```

## Troubleshooting

### Common Issues

1. **503 Service Unavailable**
   - LLM service is not initialized
   - Check model availability with `/api/llm/models`

2. **429 Rate Limit Exceeded**
   - Too many requests in short time
   - Wait before retrying or increase rate limits

3. **404 Session Not Found**
   - Session ID doesn't exist or user doesn't have access
   - Verify session exists with `/api/chat/sessions`

4. **Streaming Connection Issues**
   - Ensure proper SSE handling in client
   - Check for network timeouts

### Debug Mode

Enable debug logging:

```bash
python backend/main.py --log-level DEBUG
```

Check logs:
```bash
tail -f logs/backend.log
```