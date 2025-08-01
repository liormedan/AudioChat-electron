# 🛠️ Audio Chat Studio - Developer Guide

מדריך מפתחים מקיף לפרויקט Audio Chat Studio.

## 🏗️ ארכיטקטורה טכנית

### סקירה כללית

המערכת בנויה על ארכיטקטורת microservices עם הפרדה ברורה בין Frontend ו-Backend:

```
┌─────────────────┐    HTTP/WebSocket    ┌─────────────────┐
│   Frontend      │◄──────────────────►│   Backend       │
│   (Electron)    │                     │   (FastAPI)     │
│                 │                     │                 │
│ • React + TS    │                     │ • Python 3.8+  │
│ • Vite          │                     │ • FastAPI       │
│ • Tailwind CSS  │                     │ • Uvicorn       │
└─────────────────┘                     └─────────────────┘
```

### Backend Architecture

```python
backend/
├── main.py                    # Entry point + server config
├── api/
│   ├── main.py               # FastAPI app + middleware
│   └── routes/               # API route handlers (future)
├── services/
│   ├── audio/
│   │   ├── editing.py        # Audio processing
│   │   └── metadata.py       # Audio analysis
│   ├── ai/
│   │   ├── llm_service.py    # LLM integration
│   │   └── command_processor.py # Natural language processing
│   └── storage/
│       └── file_upload.py    # File management
├── models/                   # Data models
└── config/                   # Configuration management
```

### Frontend Architecture

```typescript
frontend/electron-app/src/
├── main/                     # Electron main process
│   └── main.ts              # App lifecycle + window management
├── renderer/                 # React application
│   ├── components/          # Reusable UI components
│   ├── pages/              # Application pages
│   ├── services/           # API communication
│   ├── stores/             # State management (Zustand)
│   └── hooks/              # Custom React hooks
└── preload/                 # Secure IPC bridge
    └── preload.ts
```

## 🤖 AI Chat System

### Overview

The AI Chat System is a comprehensive conversational AI interface that allows users to interact with various AI models including local Gemma models and cloud providers. The system features session management, message history, streaming responses, and advanced security features.

### Architecture

The chat system follows a layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
├─────────────────────────────────────────────────────────────┤
│ Chat Interface │ Session Manager │ Settings Panel │ History │
├─────────────────────────────────────────────────────────────┤
│              Chat Store (Zustand State Management)          │
├─────────────────────────────────────────────────────────────┤
│                   Chat API Service                          │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                         │
├─────────────────────────────────────────────────────────────┤
│    Chat API    │  Session API  │  Message API  │  Export    │
├─────────────────────────────────────────────────────────────┤
│ Chat Service │ Session Service │ History Service │ Security  │
├─────────────────────────────────────────────────────────────┤
│              LLM Service │ Cache Service │ Audit Service     │
├─────────────────────────────────────────────────────────────┤
│                      SQLite Database                        │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

#### Backend Services

**Chat Service** (`backend/services/ai/chat_service.py`)
- Handles message processing and AI model communication
- Manages conversation context and streaming responses
- Integrates with LLM service for model interactions

**Session Service** (`backend/services/ai/session_service.py`)
- Manages chat session lifecycle (create, read, update, delete)
- Handles session metadata and user associations
- Provides session listing and filtering capabilities

**Chat History Service** (`backend/services/ai/chat_history_service.py`)
- Stores and retrieves message history
- Provides search functionality across messages
- Handles message export in various formats

**Security Service** (`backend/services/ai/chat_security_service.py`)
- Implements rate limiting and input sanitization
- Validates session access permissions
- Provides audit logging for security events

#### Frontend Components

**Chat Interface** (`frontend/electron-app/src/renderer/components/chat/chat-interface.tsx`)
- Main chat UI with message display and input
- Handles real-time message updates and streaming
- Integrates with session management and settings

**Session Manager** (`frontend/electron-app/src/renderer/components/chat/session-manager.tsx`)
- Session creation, editing, and deletion
- Session search and filtering
- Session archiving and organization

**Message List** (`frontend/electron-app/src/renderer/components/chat/message-list.tsx`)
- Virtual scrolling for performance with large conversations
- Message rendering with markdown support
- Copy-to-clipboard and message actions

**Settings Panel** (`frontend/electron-app/src/renderer/components/chat/settings-panel.tsx`)
- Model parameter configuration (temperature, max_tokens, etc.)
- Preset management for different use cases
- Real-time parameter preview

### API Endpoints

#### Chat Endpoints

```http
POST /api/chat/send
Content-Type: application/json

{
  "session_id": "string",
  "message": "string",
  "user_id": "string (optional)"
}
```

```http
POST /api/chat/stream
Content-Type: application/json

{
  "session_id": "string", 
  "message": "string",
  "user_id": "string (optional)"
}
```

#### Session Management

```http
GET /api/chat/sessions?user_id=string
POST /api/chat/sessions
GET /api/chat/sessions/{session_id}
PUT /api/chat/sessions/{session_id}
DELETE /api/chat/sessions/{session_id}
```

#### Message Management

```http
GET /api/chat/sessions/{session_id}/messages?limit=50&offset=0
POST /api/chat/sessions/{session_id}/messages
GET /api/chat/search?query=string&user_id=string&session_id=string
POST /api/chat/export/{session_id}
```

### Data Models

#### ChatSession
```python
@dataclass
class ChatSession:
    id: str
    title: str
    model_id: str
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int
    is_archived: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### Message
```python
@dataclass
class Message:
    id: str
    session_id: str
    content: str
    timestamp: datetime
    role: MessageRole  # USER, ASSISTANT, SYSTEM
    type: MessageType  # TEXT, AUDIO, IMAGE, FILE
    model_id: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### ChatResponse
```python
@dataclass
class ChatResponse:
    content: str
    model_id: str
    tokens_used: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### Database Schema

```sql
-- Chat Sessions
CREATE TABLE chat_sessions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    model_id TEXT NOT NULL,
    user_id TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    message_count INTEGER DEFAULT 0,
    is_archived BOOLEAN DEFAULT FALSE,
    metadata TEXT DEFAULT '{}'
);

-- Chat Messages
CREATE TABLE chat_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    model_id TEXT,
    tokens_used INTEGER,
    response_time REAL,
    metadata TEXT DEFAULT '{}',
    FOREIGN KEY (session_id) REFERENCES chat_sessions (id) ON DELETE CASCADE
);

-- Performance Indexes
CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_updated_at ON chat_sessions(updated_at);
CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_timestamp ON chat_messages(timestamp);
```

### Security Features

#### Rate Limiting
- 5 requests per minute per user for chat endpoints
- Configurable limits per endpoint
- IP-based and user-based limiting

#### Input Sanitization
```python
def sanitize_input(input_text: str) -> str:
    """Remove potentially harmful content from user input"""
    # Remove script tags, javascript: URLs, etc.
    return sanitized_text
```

#### Session Access Control
```python
def validate_session_access(session_id: str, user_id: str) -> bool:
    """Validate that user has access to the session"""
    # Check session ownership and permissions
    return has_access
```

#### Audit Logging
All chat operations are logged with:
- User ID and IP address
- Action performed
- Timestamp and duration
- Success/failure status
- Error messages (if any)

### Performance Optimizations

#### Backend Caching
- In-memory caching for active sessions
- Database connection pooling
- Batch operations for message storage

#### Frontend Optimizations
- Virtual scrolling for large message lists
- React.memo for expensive components
- Debounced search and input handling
- Lazy loading for session history

### Development Workflow

#### Adding New Chat Features

1. **Backend Development**
```python
# 1. Add service method
class ChatService:
    def new_feature(self, param: str) -> Result:
        # Implementation
        pass

# 2. Add API endpoint
@app.post('/api/chat/new-feature')
async def new_feature_endpoint(request: Request):
    # Implementation
    pass

# 3. Add tests
def test_new_feature():
    # Test implementation
    pass
```

2. **Frontend Development**
```typescript
// 1. Add API service method
class ChatApiService {
  async newFeature(param: string): Promise<Result> {
    // Implementation
  }
}

// 2. Add store action
const useChatStore = create((set) => ({
  newFeature: async (param: string) => {
    // Implementation
  }
}));

// 3. Add component
export const NewFeatureComponent: React.FC = () => {
  // Implementation
};
```

#### Testing Chat Features

```bash
# Backend tests
python -m pytest tests/integration/test_chat_integration.py
python -m pytest tests/unit/test_chat_service.py

# Frontend tests
cd frontend/electron-app
npm run test:chat

# E2E tests
npm run test:e2e -- --grep "chat"
```

## 🔧 Development Setup

### Prerequisites

```bash
# Required
Python 3.8+
Node.js 16+
Git

# Optional but recommended
VS Code
Python extension for VS Code
TypeScript extension for VS Code
```

### Initial Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd Audio-Chat-Studio

# 2. Run automated setup
scripts\setup.bat

# 3. Verify installation
scripts\utils\health-check.bat
```

### Manual Setup (if automated fails)

```bash
# Backend setup
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd frontend\electron-app
npm install
cd ..\..

# Verify
python -c "from backend.api.main import create_app; print('Backend OK')"
cd frontend\electron-app && npm run test:backend
```

## 🚀 Development Workflow

### Starting Development Environment

```bash
# Full development mode (recommended)
scripts\start-dev.bat

# Backend only
python backend\main.py --reload --log-level DEBUG

# Frontend only
cd frontend\electron-app
npm run dev
```

### Code Structure Guidelines

#### Backend (Python)

```python
# File naming: snake_case
# Class naming: PascalCase
# Function naming: snake_case
# Constants: UPPER_CASE

# Example service structure
class AudioMetadataService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from audio file."""
        try:
            # Implementation
            return {"success": True, "data": metadata}
        except Exception as e:
            self.logger.error(f"Metadata extraction failed: {e}")
            return {"success": False, "error": str(e)}
```

#### Frontend (TypeScript)

```typescript
// File naming: kebab-case
// Component naming: PascalCase
// Function naming: camelCase
// Constants: UPPER_CASE

// Example service structure
export class AudioUploadService {
  private baseUrl: string;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  async uploadFile(file: File): Promise<UploadResult> {
    try {
      // Implementation
      return { success: true, data: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
}
```

### API Development

#### Adding New Endpoints

1. **Define the endpoint in `backend/api/main.py`:**

```python
@app.post('/api/new-feature')
async def new_feature_endpoint(request: Request):
    try:
        data = await request.json()
        # Process data
        return JSONResponse(content={"success": True, "result": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

2. **Add corresponding frontend service:**

```typescript
// In appropriate service file
async newFeature(data: any): Promise<ApiResult> {
  try {
    const response = await fetch(`${this.baseUrl}/api/new-feature`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return await response.json();
  } catch (error) {
    return { success: false, error: error.message };
  }
}
```

3. **Test the endpoint:**

```bash
# Start development server
scripts\start-dev.bat

# Test via Swagger UI
# http://127.0.0.1:5000/docs

# Or via curl
curl -X POST http://127.0.0.1:5000/api/new-feature \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### Frontend Development

#### Adding New Components

```typescript
// components/new-component.tsx
import React from 'react';

interface NewComponentProps {
  title: string;
  onAction: () => void;
}

export const NewComponent: React.FC<NewComponentProps> = ({ 
  title, 
  onAction 
}) => {
  return (
    <div className="p-4 border rounded-lg">
      <h3 className="text-lg font-semibold">{title}</h3>
      <button 
        onClick={onAction}
        className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Action
      </button>
    </div>
  );
};
```

#### State Management

```typescript
// stores/new-store.ts
import { create } from 'zustand';

interface NewState {
  data: any[];
  loading: boolean;
  setData: (data: any[]) => void;
  setLoading: (loading: boolean) => void;
}

export const useNewStore = create<NewState>((set) => ({
  data: [],
  loading: false,
  setData: (data) => set({ data }),
  setLoading: (loading) => set({ loading }),
}));
```

## 🧪 Testing

### Backend Testing

```python
# Test individual services
python -c "
from backend.services.audio.metadata import AudioMetadataService
service = AudioMetadataService()
print('Service initialized successfully')
"

# Test API endpoints
python -c "
from backend.api.main import create_app
app = create_app()
print(f'App created with {len(app.routes)} routes')
"
```

### Frontend Testing

```bash
# Type checking
cd frontend\electron-app
npm run type-check

# Build testing
npm run build

# Backend connection testing
npm run test:backend
```

### Integration Testing

```bash
# Full system health check
scripts\utils\health-check.bat

# Manual integration test
# 1. Start system: scripts\start-dev.bat
# 2. Open: http://127.0.0.1:5000/docs
# 3. Test file upload endpoint
# 4. Check frontend connection
```

## 📦 Build & Deployment

### Development Build

```bash
# Frontend only
cd frontend\electron-app
npm run build

# Backend only
python -m PyInstaller backend\main.py
```

### Production Build

```bash
# Full production build
scripts\build.bat

# This creates:
# - py_build/dist/audio-chat-studio-backend.exe
# - frontend/electron-app/dist/
# - frontend/electron-app/release/ (optional)
```

### Deployment Options

#### Standalone Executable
```bash
# After running scripts\build.bat
# Distribute: py_build/dist/audio-chat-studio-backend.exe
# No Python installation required on target machine
```

#### Electron App Package
```bash
cd frontend\electron-app
npm run package
# Creates installer in release/ directory
```

## 🔍 Debugging

### Backend Debugging

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Start with debug mode
python backend\main.py --log-level DEBUG

# Check logs
type logs\backend.log
```

### Frontend Debugging

```bash
# Start with DevTools
scripts\start-dev.bat

# In Electron app: Ctrl+Shift+I for DevTools
# Check Network tab for API calls
# Check Console for errors
```

### Common Issues

#### Import Errors
```python
# Ensure PYTHONPATH includes backend directory
import sys
sys.path.insert(0, 'backend')
```

#### CORS Issues
```typescript
// Ensure proxy is configured in vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:5000',
      changeOrigin: true,
    },
  },
}
```

#### Port Conflicts
```bash
# Check what's using ports
netstat -an | find "5000"

# Kill processes if needed
taskkill /f /im python.exe
```

## 🎨 Code Style

### Python (Backend)

```python
# Use Black formatter
pip install black
black backend/

# Use type hints
def process_audio(file_path: str) -> Dict[str, Any]:
    pass

# Use docstrings
def extract_metadata(file_path: str) -> Dict[str, Any]:
    """
    Extract comprehensive metadata from audio file.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Dictionary containing metadata or error information
    """
    pass
```

### TypeScript (Frontend)

```typescript
// Use Prettier formatter
npm run lint:fix

// Use explicit types
interface AudioFile {
  id: string;
  name: string;
  size: number;
  uploadedAt: Date;
}

// Use async/await
const uploadFile = async (file: File): Promise<UploadResult> => {
  try {
    const result = await apiService.upload(file);
    return result;
  } catch (error) {
    throw new Error(`Upload failed: ${error.message}`);
  }
};
```

## 🔧 Configuration

### Environment Variables

```bash
# .env file (create if needed)
API_HOST=127.0.0.1
API_PORT=5000
LOG_LEVEL=INFO
DEBUG=false
```

### Backend Configuration

```python
# backend/config/settings.py
class Settings:
    api_host: str = "127.0.0.1"
    api_port: int = 5000
    log_level: str = "INFO"
    debug: bool = False
```

### Frontend Configuration

```typescript
// src/config/constants.ts
export const API_CONFIG = {
  BASE_URL: process.env.NODE_ENV === 'development' 
    ? 'http://127.0.0.1:5000' 
    : '',
  TIMEOUT: 30000,
};
```

## 📚 Additional Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Electron Documentation](https://www.electronjs.org/docs)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)

### Tools
- [Postman](https://www.postman.com/) - API testing
- [VS Code](https://code.visualstudio.com/) - IDE
- [Git](https://git-scm.com/) - Version control

### Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts\setup.bat` | Initial setup | One-time installation |
| `scripts\start.bat` | Normal startup | Regular development |
| `scripts\start-dev.bat` | Development mode | Hot reload + debug |
| `scripts\start-prod.bat` | Production mode | Built files |
| `scripts\build.bat` | Build for production | Create executables |
| `scripts\stop.bat` | Stop all services | Clean shutdown |
| `scripts\utils\health-check.bat` | System health | Diagnostics |
| `scripts\utils\cleanup.bat` | Clean temp files | Maintenance |

---

**Happy Coding!** 🚀👨‍💻👩‍💻
### Ch
at System Troubleshooting Guide

#### Common Chat Issues

**Chat messages not sending**
```bash
# Check backend logs
type logs\backend.log | findstr "chat"

# Verify chat service status
curl http://127.0.0.1:5000/api/chat/health

# Test database connection
python -c "from backend.services.database.connection import get_db_connection; print('DB OK' if get_db_connection() else 'DB Failed')"
```

**Session not loading**
```bash
# Check session service
curl http://127.0.0.1:5000/api/chat/sessions

# Verify database tables
python -c "from backend.services.ai.session_service import SessionService; print(SessionService().list_sessions())"
```

**Streaming responses not working**
```bash
# Test SSE endpoint
curl -N http://127.0.0.1:5000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"session_id":"test","message":"Hello"}'

# Check WebSocket connection in browser DevTools
```

**Performance issues**
```bash
# Run performance tests
python tests/performance/run_performance_tests.py

# Check database performance
python backend/services/database/database_optimization_example.py

# Monitor memory usage
python -c "import psutil; print(f'Memory: {psutil.virtual_memory().percent}%')"
```

#### Chat System Architecture Diagrams

**Message Flow Diagram**
```
User Input → Chat Interface → Chat Store → API Service → Backend
    ↓              ↓             ↓           ↓           ↓
Message UI ← State Update ← Response ← JSON/SSE ← Chat Service
    ↓              ↓             ↓           ↓           ↓
Database ← History Service ← Session Service ← LLM Service ← AI Model
```

**Session Management Flow**
```
Session Creation:
Frontend → POST /api/chat/sessions → SessionService → Database
    ↓                                      ↓              ↓
Session UI ← Session Object ← JSON Response ← Session Data

Message Processing:
Frontend → POST /api/chat/send → ChatService → LLM Service
    ↓                              ↓             ↓
Message UI ← Streaming Response ← SSE Stream ← AI Response
    ↓                              ↓             ↓
History ← Database Storage ← Message Object ← Processed Response
```

**Security Flow**
```
Request → Rate Limiter → Input Sanitizer → Session Validator
   ↓           ↓              ↓                ↓
Response ← Audit Logger ← Security Service ← Access Control
```

### Chat Component Documentation

#### Core Components Props and Usage

**ChatInterface Component**
```typescript
interface ChatInterfaceProps {
  sessionId?: string;
  initialMessage?: string;
  onSessionChange?: (sessionId: string) => void;
  className?: string;
}

// Usage
<ChatInterface 
  sessionId="session-123"
  onSessionChange={(id) => console.log('Session changed:', id)}
  className="h-full"
/>
```

**MessageList Component**
```typescript
interface MessageListProps {
  messages: Message[];
  loading?: boolean;
  onMessageAction?: (messageId: string, action: string) => void;
  virtualScrolling?: boolean;
}

// Usage
<MessageList 
  messages={messages}
  loading={isLoading}
  onMessageAction={handleMessageAction}
  virtualScrolling={true}
/>
```

**SessionManager Component**
```typescript
interface SessionManagerProps {
  currentSessionId?: string;
  onSessionSelect: (sessionId: string) => void;
  onSessionCreate: () => void;
  onSessionDelete: (sessionId: string) => void;
}

// Usage
<SessionManager 
  currentSessionId={currentSession}
  onSessionSelect={setCurrentSession}
  onSessionCreate={createNewSession}
  onSessionDelete={deleteSession}
/>
```

**SettingsPanel Component**
```typescript
interface SettingsPanelProps {
  modelSettings: ModelSettings;
  onSettingsChange: (settings: ModelSettings) => void;
  presets?: SettingsPreset[];
  onPresetSave?: (preset: SettingsPreset) => void;
}

// Usage
<SettingsPanel 
  modelSettings={settings}
  onSettingsChange={updateSettings}
  presets={availablePresets}
  onPresetSave={savePreset}
/>
```

### Performance Optimization Guidelines

#### Backend Performance

**Database Optimization**
```python
# Use connection pooling
from backend.services.database.connection import get_db_pool

# Batch operations
def batch_insert_messages(messages: List[Message]):
    with get_db_pool() as conn:
        conn.executemany(INSERT_MESSAGE_SQL, messages)

# Use indexes for common queries
CREATE INDEX idx_messages_session_timestamp ON chat_messages(session_id, timestamp);
```

**Caching Strategy**
```python
from functools import lru_cache
import redis

# In-memory caching for active sessions
@lru_cache(maxsize=100)
def get_session_cache(session_id: str):
    return session_data

# Redis for distributed caching
redis_client = redis.Redis(host='localhost', port=6379, db=0)
```

#### Frontend Performance

**Virtual Scrolling for Large Message Lists**
```typescript
import { FixedSizeList as List } from 'react-window';

const MessageVirtualList: React.FC = ({ messages }) => {
  const Row = ({ index, style }) => (
    <div style={style}>
      <MessageComponent message={messages[index]} />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={messages.length}
      itemSize={80}
    >
      {Row}
    </List>
  );
};
```

**Debounced Search and Input**
```typescript
import { useDebouncedCallback } from 'use-debounce';

const SearchInput: React.FC = () => {
  const debouncedSearch = useDebouncedCallback(
    (value: string) => {
      performSearch(value);
    },
    300
  );

  return (
    <input 
      onChange={(e) => debouncedSearch(e.target.value)}
      placeholder="Search messages..."
    />
  );
};
```

**React.memo for Expensive Components**
```typescript
const MessageComponent = React.memo<MessageProps>(({ message }) => {
  return (
    <div className="message">
      {/* Expensive rendering logic */}
    </div>
  );
}, (prevProps, nextProps) => {
  return prevProps.message.id === nextProps.message.id &&
         prevProps.message.content === nextProps.message.content;
});
```