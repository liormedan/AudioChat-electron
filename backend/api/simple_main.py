"""
Simple FastAPI Audio Server
שרת פשוט ללא תלויות מורכבות
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Audio Chat Studio API - Simple",
    description="Simple API for audio processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class CommandRequest(BaseModel):
    command: str
    file_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class AudioEditRequest(BaseModel):
    input_file: str
    operation: str
    params: Dict[str, Any]

# Simple file storage
uploaded_files = {}

# --- Health Check ---
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Audio Chat Studio API - Simple",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "api": "active",
            "simple_mode": True
        }
    }

# --- File Upload Endpoints ---
@app.post("/api/audio/upload")
async def upload_audio_file(file: UploadFile = File(...)):
    """Upload an audio file"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.mp3', '.wav', '.flac', '.ogg', '.m4a')):
            raise HTTPException(status_code=400, detail="Unsupported file format")
        
        # Create uploads directory
        upload_dir = Path("../../data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Store file info
        file_id = str(len(uploaded_files) + 1)
        uploaded_files[file_id] = {
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size": len(content)
        }
        
        return {
            "success": True,
            "file_id": file_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size": len(content)
        }
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/files")
async def list_audio_files():
    """List all uploaded audio files"""
    return {
        "success": True,
        "files": list(uploaded_files.values())
    }

@app.get("/api/audio/files/{file_id}")
async def get_file_info(file_id: str):
    """Get information about a specific file"""
    if file_id not in uploaded_files:
        raise HTTPException(status_code=404, detail="File not found")
    
    return {
        "success": True,
        **uploaded_files[file_id]
    }

# --- Command Processing Endpoints ---
@app.post("/api/audio/command/interpret")
async def interpret_audio_command(request: CommandRequest):
    """Simple command interpretation"""
    return {
        "success": True,
        "interpretation": {
            "command": request.command,
            "operation": "mock_operation",
            "params": {"mock": True},
            "confidence": 0.8
        }
    }

@app.post("/api/audio/command/execute")
async def execute_audio_command(request: CommandRequest):
    """Simple command execution"""
    return {
        "success": True,
        "result": {
            "operation": "mock_execution",
            "input_file": request.file_id,
            "output_file": "mock_output.wav",
            "processing_time": 1.5
        }
    }

@app.get("/api/audio/command/help")
async def get_command_help():
    """Get help information for commands"""
    return {
        "success": True,
        "commands": [
            {
                "name": "trim",
                "description": "Trim audio file",
                "example": "trim audio from 10 seconds to 30 seconds"
            },
            {
                "name": "volume",
                "description": "Adjust volume",
                "example": "increase volume by 10dB"
            },
            {
                "name": "normalize",
                "description": "Normalize audio",
                "example": "normalize audio to -3dB"
            }
        ]
    }

# --- Direct Audio Processing ---
@app.post("/api/audio/execute-command")
async def execute_direct_audio_command(request: AudioEditRequest):
    """Simple direct audio command execution"""
    return {
        "success": True,
        "output_file": f"processed_{request.input_file}",
        "processing_time": 2.0,
        "operation": request.operation,
        "params": request.params
    }

if __name__ == "__main__":
    # Create data directories
    os.makedirs("../../data/uploads", exist_ok=True)
    
    # Run the server
    uvicorn.run(
        "simple_main:app",
        host="127.0.0.1",
        port=5000,
        reload=True,
        log_level="info"
    )