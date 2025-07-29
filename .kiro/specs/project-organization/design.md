# Design Document

## Overview

המטרה היא לארגן מחדש את פרויקט Audio Chat Studio כך שיהיה מבנה ברור ומסודר עם הפרדה נכונה בין הבקאנד והפרונטאנד, קבצי הפעלה פשוטים ונוחים, וניהול dependencies מסודר.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Start Scripts │    │   Frontend      │    │   Backend       │
│   (Batch Files) │───▶│   (Electron)    │───▶│   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Environment   │    │   Vite Dev      │    │   Services      │
│   Management    │    │   Server        │    │   Layer         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Backend Architecture

```
backend/
├── main.py                 # Main entry point
├── api/
│   ├── main.py            # FastAPI app configuration
│   └── routes/            # API route handlers
├── services/              # Business logic services
├── models/                # Data models
└── config/                # Configuration management
```

### Frontend Architecture

```
frontend/electron-app/
├── src/
│   ├── main/              # Electron main process
│   ├── renderer/          # React renderer process
│   └── preload/           # Preload scripts
├── package.json           # Dependencies and scripts
└── vite.config.ts         # Build configuration
```

## Components and Interfaces

### 1. Backend Entry Point (backend/main.py)

**Purpose:** נקודת כניסה ראשית לבקאנד שמפעילה את שרת FastAPI

**Interface:**
```python
def main():
    """Main entry point for the backend server"""
    
def start_server(host: str = "127.0.0.1", port: int = 5000):
    """Start the FastAPI server with proper configuration"""
    
def setup_logging():
    """Configure logging for the application"""
```

### 2. FastAPI Application (backend/api/main.py)

**Purpose:** הגדרת האפליקציה FastAPI עם כל ה-routes וה-middleware

**Interface:**
- יישאר כמו שהוא עכשיו אבל יועבר לפונקציה create_app()
- יתווסף configuration management
- יתווסף proper error handling

### 3. Startup Scripts

**Purpose:** קבצי הפעלה פשוטים ונוחים למשתמש

**Scripts:**
- `scripts/start.bat` - הפעלה מלאה של המערכת
- `scripts/start-dev.bat` - הפעלה במצב פיתוח
- `scripts/setup.bat` - התקנה ראשונית
- `scripts/stop.bat` - עצירת המערכת

### 4. Environment Management

**Purpose:** ניהול סביבות פיתוח וייצור

**Components:**
- Virtual environment activation
- Dependency checking and installation
- Environment variable management
- Port availability checking

## Data Models

### Configuration Model

```python
class AppConfig:
    api_host: str = "127.0.0.1"
    api_port: int = 5000
    admin_port: int = 5001
    frontend_port: int = 5174
    debug: bool = False
    log_level: str = "INFO"
```

### Server Status Model

```python
class ServerStatus:
    name: str
    status: str  # "running", "stopped", "error"
    port: int
    pid: Optional[int]
    uptime: Optional[float]
```

## Error Handling

### Backend Error Handling

1. **Startup Errors:**
   - Port already in use
   - Missing dependencies
   - Configuration errors

2. **Runtime Errors:**
   - Service failures
   - File system errors
   - Network errors

### Frontend Error Handling

1. **Connection Errors:**
   - Backend not available
   - Network timeouts
   - CORS issues

2. **Build Errors:**
   - Missing dependencies
   - TypeScript errors
   - Asset loading failures

### Script Error Handling

1. **Environment Errors:**
   - Virtual environment not found
   - Python not installed
   - Node.js not installed

2. **Process Errors:**
   - Failed to start servers
   - Port conflicts
   - Permission issues

## Testing Strategy

### Unit Tests

1. **Backend Services:**
   - Test each service independently
   - Mock external dependencies
   - Validate business logic

2. **API Endpoints:**
   - Test request/response handling
   - Validate error responses
   - Test authentication/authorization

### Integration Tests

1. **Full Workflow Tests:**
   - Test complete user workflows
   - Validate frontend-backend communication
   - Test file upload and processing

2. **Startup Tests:**
   - Test script execution
   - Validate server startup
   - Test environment setup

### End-to-End Tests

1. **User Journey Tests:**
   - Test complete user interactions
   - Validate UI functionality
   - Test audio processing workflows

## Deployment Considerations

### Development Environment

- Hot reload for both frontend and backend
- Detailed logging and debugging
- Easy script execution
- Fast iteration cycles

### Production Environment

- Optimized builds
- Proper error handling
- Security considerations
- Performance monitoring

## Migration Strategy

### Phase 1: Backend Reorganization
1. Create new backend/main.py entry point
2. Refactor backend/api/main.py to use create_app pattern
3. Update import paths
4. Test backend functionality

### Phase 2: Script Improvement
1. Create new startup scripts
2. Add environment checking
3. Add dependency management
4. Test script execution

### Phase 3: Frontend Integration
1. Update frontend configuration
2. Update API endpoints
3. Test frontend-backend communication
4. Validate full application flow

### Phase 4: Documentation and Testing
1. Update documentation
2. Add comprehensive tests
3. Validate all functionality
4. Performance testing