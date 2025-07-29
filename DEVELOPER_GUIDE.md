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