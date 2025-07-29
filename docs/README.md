# 🎵 Audio Chat Studio

**AI-Powered Audio Editing Through Natural Language Commands**

Audio Chat Studio is a comprehensive audio editing platform that allows users to edit audio files using natural language commands. The system combines modern web technologies with powerful AI to create an intuitive audio editing experience.

---

## 🏗️ System Architecture

The project consists of multiple integrated components:

### 🖥️ **Backend Services**
- **FastAPI Server** (`fastapi_server.py`) - Main API server for audio processing
- **Admin Interface** (`admin_server.py`) - System monitoring and management
- **Audio Processing Services** - Advanced audio editing with pydub, librosa, and AI

### 🌐 **Frontend Applications**
- **Electron App** (`electron-app/`) - Modern React/TypeScript desktop application
-
- **Admin Dashboard** - Real-time system monitoring interface

### 🤖 **AI Integration**
- **Natural Language Processing** - Command interpretation using LLM
- **Audio Intelligence** - Smart audio analysis and suggestions
- **Command Mapping** - Automatic translation of text to audio operations

---

## 🚀 Quick Start (Recommended)

### One-Click Setup & Launch
```bash
# 1. Install all dependencies
scripts\setup\install_dependencies.bat

# 2. Quick system check
scripts\setup\quick_test.bat

# 3. Launch everything (recommended)
start.bat

# OR use the organized scripts:
scripts\start\start_all.bat
```

### Available Interfaces
After running `start_all.bat`, access:

| Interface | URL | Description |
|-----------|-----|-------------|
| 🎵 **Main App** | http://127.0.0.1:3000 | Audio editing interface |
| 📚 **API Docs** | http://127.0.0.1:5000/docs | Interactive API documentation |
| 🛠️ **Admin Panel** | http://127.0.0.1:5001 | System monitoring & management |
| 🔧 **API Server** | http://127.0.0.1:5000 | Backend API endpoints |

### LLM Provider API Endpoints
- **POST `/api/llm/set-api-key`** - save API key for a provider
- **POST `/api/llm/test-connection`** - test provider connection status

---

## 📁 Project Structure

```
Audio-Chat-Studio/
├── 🚀 Quick Launch Files
│   ├── start_all.bat              # Launch entire system
│   ├── start_api_only.bat         # API server only
│   ├── start_admin_only.bat       # Admin interface only
│   ├── start_electron_only.bat    # Electron app only
│   ├── stop_all.bat               # Stop all services
│   ├── install_dependencies.bat   # Setup everything
│   ├── quick_test.bat             # System health check
│   └── check_status.bat           # Service status check
│
├── 🖥️ Backend Services
│   ├── fastapi_server.py          # Main FastAPI server
│   ├── admin_server.py            # Admin interface server
│   └── my_audio_app/              # Audio processing services
│       ├── src/services/          # Core audio services
│       │   ├── audio_editing_service.py
│       │   ├── advanced_audio_editing_service.py
│       │   ├── audio_command_interpreter.py
│       │   ├── audio_command_processor.py
│       │   ├── llm_service.py
│       │   └── file_upload_service.py
│       └── main.py                # PyQt6 application
│
├── 🌐 Frontend Applications
│   ├── electron-app/              # Modern React/TypeScript app
│   │   ├── src/renderer/
│   │   │   ├── components/        # React components
│   │   │   ├── pages/             # Application pages
│   │   │   ├── hooks/             # Custom React hooks
│   │   │   └── stores/            # State management
│   │   └── package.json
│   └── templates/                 # Admin interface templates
│       └── admin_dashboard.html
│
├── 📊 Data & Logs
│   ├── uploads/                   # Uploaded audio files
│   ├── logs/                      # System logs
│   └── temp/                      # Temporary processing files
│
└── 📚 Documentation
    ├── README_BAT_FILES.md        # BAT files usage guide
    ├── STARTUP_GUIDE.md           # Detailed startup instructions
    └── electron-app/buildocs/     # Development documentation
        ├── BUILD_ROADMAP_CORRECTED.md
        ├── WEEK2_DAY5_COMPLETION.md
        └── WEEK3_DAY5_COMPLETION.md
```

---

## ✨ Key Features

### 🎯 **Natural Language Audio Editing**
- **Voice Commands**: "Remove background noise from the first 30 seconds"
- **Smart Interpretation**: AI understands context and intent
- **Parameter Extraction**: Automatic detection of time ranges, levels, etc.

### 🔧 **Advanced Audio Processing**
- **Noise Reduction**: AI-powered background noise removal
- **Audio Enhancement**: Normalization, EQ, compression
- **Format Support**: MP3, WAV, FLAC, OGG, M4A
- **Batch Processing**: Multiple files simultaneously

### 🖥️ **Interactive Editing Interface**
- **Real-time Preview**: Before/after comparison
- **Undo/Redo System**: Full edit history management
- **Visual Waveforms**: Interactive audio visualization
- **Quick Actions**: One-click common operations

### 📊 **System Monitoring**
- **Real-time Metrics**: CPU, memory, disk usage
- **File Management**: Upload, download, delete files
- **Live Logs**: System activity monitoring
- **Performance Charts**: Visual performance tracking

---

## 🛠️ Development Modes

### For API Development
```bash
start_api_only.bat
# Access: http://127.0.0.1:5000/docs
```

### For Frontend Development
```bash
start_electron_only.bat
# Access: http://127.0.0.1:3000
```

### For System Administration
```bash
start_admin_only.bat
# Access: http://127.0.0.1:5001
```

### Full System Demo
```bash
start_all.bat
# All interfaces available
```

---

## 🔧 Technical Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydub** - Audio manipulation
- **Librosa** - Audio analysis
- **OpenAI/LLM** - Natural language processing

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Electron** - Desktop application
- **Tailwind CSS** - Styling
- **Zustand** - State management

### Audio Processing
- **FFmpeg** - Audio codec support
- **NumPy/SciPy** - Numerical processing
- **Soundfile** - Audio I/O
- **Noisereduce** - Noise reduction

---

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space

### Recommended for Best Performance
- **RAM**: 16GB or more
- **CPU**: Multi-core processor
- **Storage**: SSD for faster file processing
- **Audio**: Dedicated audio interface (optional)

---

## 🚨 Troubleshooting

### Common Issues & Solutions

#### ❌ "Python not found"
```bash
# Install Python 3.8+ from: https://python.org
# Ensure Python is in PATH
```

#### ❌ "Node.js not found"
```bash
# Install Node.js from: https://nodejs.org
# Restart terminal after installation
```

#### ❌ "Port already in use"
```bash
stop_all.bat          # Stop all services
start_all.bat         # Restart everything
```

#### ❌ "Dependencies missing"
```bash
install_dependencies.bat    # Reinstall everything
quick_test.bat             # Verify installation
```

#### ❌ "Audio processing fails"
```bash
# Check admin panel: http://127.0.0.1:5001
# View logs in logs/ directory
# Ensure audio files are supported formats
```

---

## 📊 Monitoring & Logs

### Real-time Monitoring
Visit the admin dashboard at http://127.0.0.1:5001 for:
- System resource usage
- Active connections
- Processing statistics
- File management
- Live log viewing

### Log Files
```
logs/
├── api_server.log      # Main API server logs
├── admin_server.log    # Admin interface logs
└── electron_app.log    # Frontend application logs
```

### Health Checks
```bash
check_status.bat        # Check all services
quick_test.bat         # Comprehensive system test
```

---

## 🤝 Development Workflow

### Setting Up Development Environment
1. **Clone repository**
2. **Run setup**: `install_dependencies.bat`
3. **Test system**: `quick_test.bat`
4. **Start development**: `start_all.bat`

### Development Guidelines
- Follow the roadmap in `electron-app/buildocs/`
- Use the testing interface for API development
- Monitor system performance via admin panel
- Check logs regularly during development

### Contributing
1. Check current development status in `buildocs/`
2. Use the interactive testing tools
3. Monitor system health during development
4. Document new features and APIs

---

## 📚 Additional Resources

- **[BAT Files Guide](README_BAT_FILES.md)** - Detailed usage of automation scripts
- **[Startup Guide](STARTUP_GUIDE.md)** - Step-by-step setup instructions
- **[Build Roadmap](electron-app/buildocs/BUILD_ROADMAP_CORRECTED.md)** - Development timeline
- **[API Documentation](http://127.0.0.1:5000/docs)** - Interactive API docs (when server is running)

---

## 🎉 Getting Started Now

Ready to experience AI-powered audio editing?

```bash
# One command to rule them all:
start_all.bat
```

Then visit http://127.0.0.1:3000 and start editing audio with natural language!

---

**Built with ❤️ for the future of audio editing**
