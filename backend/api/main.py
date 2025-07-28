"""
FastAPI Audio Chat Server
שרת מבוסס FastAPI לעיבוד אודיו עם תמיכה מלאה ב-async
"""

import os
import logging
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Import our services
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.file_upload_service import FileUploadService
from services.audio_editing_service import AudioEditingService
from services.advanced_audio_editing_service import AdvancedAudioEditingService
from services.llm_service import LLMService
from services.audio_metadata_service import AudioMetadataService
from services.audio_command_interpreter import AudioCommandInterpreter
from services.audio_command_processor import AudioCommandProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Audio Chat Studio API",
    description="API for AI-powered audio editing through natural language commands",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads")
file_upload_service = FileUploadService(upload_directory=upload_dir)
audio_editing_service = AudioEditingService()
advanced_audio_editing_service = AdvancedAudioEditingService()
llm_service = LLMService()
audio_metadata_service = AudioMetadataService()
audio_command_interpreter = AudioCommandInterpreter(llm_service)
audio_command_processor = AudioCommandProcessor(
    llm_service=llm_service,
    audio_editing_service=audio_editing_service,
    audio_metadata_service=audio_metadata_service
)

# Pydantic models for request/response
class CommandRequest(BaseModel):
    command: str
    file_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class CommandValidationRequest(BaseModel):
    command: str
    file_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class CommandSuggestionsRequest(BaseModel):
    partial_command: str = ""
    file_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class AudioEditRequest(BaseModel):
    input_file: str
    operation: str
    params: Dict[str, Any]

# --- Health Check ---
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Audio Chat Studio API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "file_upload": "active",
            "audio_editing": "active",
            "command_interpreter": "active",
            "advanced_editing": "active"
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
        
        # Read file content
        file_content = await file.read()
        
        # Save file
        result = file_upload_service.save_uploaded_file(file_content, file.filename)
        
        if result.get('success'):
            return {
                "success": True,
                "file_id": result['file_id'],
                "filename": result['filename'],
                "file_path": result['file_path'],
                "file_size": result.get('file_size', 0)
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Upload failed'))
            
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/files")
async def list_audio_files():
    """List all uploaded audio files"""
    try:
        files = file_upload_service.list_files()
        return {
            "success": True,
            "files": files
        }
    except Exception as e:
        logger.error(f"List files error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/files/{file_id}")
async def get_file_info(file_id: str):
    """Get information about a specific file"""
    try:
        file_info = file_upload_service.get_file_info(file_id)
        if file_info and file_info.get('success'):
            return file_info
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Get file info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/files/{file_id}/download")
async def download_file(file_id: str):
    """Download a file"""
    try:
        file_info = file_upload_service.get_file_info(file_id)
        if not file_info or not file_info.get('success'):
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = file_info['file_path']
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            path=file_path,
            filename=file_info['filename'],
            media_type='application/octet-stream'
        )
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/audio/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file"""
    try:
        result = file_upload_service.delete_file(file_id)
        if result.get('success'):
            return {"success": True, "message": "File deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Audio Metadata Endpoints ---
@app.get("/api/audio/metadata/{file_id}")
async def get_audio_metadata(file_id: str):
    """Get audio file metadata"""
    try:
        file_info = file_upload_service.get_file_info(file_id)
        if not file_info or not file_info.get('success'):
            raise HTTPException(status_code=404, detail="File not found")
        
        metadata = audio_editing_service.get_audio_metadata(file_info['file_path'])
        return {
            "success": True,
            "metadata": metadata
        }
    except Exception as e:
        logger.error(f"Metadata error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Command Processing Endpoints ---
@app.post("/api/audio/command/interpret")
async def interpret_audio_command(request: CommandRequest):
    """Interpret natural language audio commands"""
    try:
        # Get file path if file_id provided
        input_file = None
        if request.file_id:
            file_info = file_upload_service.get_file_info(request.file_id)
            if file_info and file_info.get('success'):
                input_file = file_info['file_path']
            else:
                raise HTTPException(status_code=404, detail="File not found")
        
        # Validate command before execution
        validation_result = await audio_command_processor.validate_command_before_execution(
            command_text=request.command,
            input_file=input_file,
            context=request.context
        )
        
        return {
            "success": True,
            "interpretation": validation_result
        }
        
    except Exception as e:
        logger.error(f"Command interpretation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to interpret command: {str(e)}")

@app.post("/api/audio/command/execute")
async def execute_audio_command(request: CommandRequest):
    """Execute natural language audio commands"""
    try:
        if not request.file_id:
            raise HTTPException(status_code=400, detail="file_id is required")
        
        # Get file information
        file_info = file_upload_service.get_file_info(request.file_id)
        if not file_info or not file_info.get('success'):
            raise HTTPException(status_code=404, detail="File not found")
        
        input_file = file_info['file_path']
        
        # Process the command
        result = await audio_command_processor.process_command(
            command_text=request.command,
            input_file=input_file,
            context=request.context
        )
        
        return {
            "success": True,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")

@app.post("/api/audio/command/suggestions")
async def get_command_suggestions(request: CommandSuggestionsRequest):
    """Get command suggestions based on partial input"""
    try:
        # Prepare context if file provided
        context = request.context.copy()
        if request.file_id:
            file_info = file_upload_service.get_file_info(request.file_id)
            if file_info and file_info.get('success'):
                context['file_info'] = file_info
        
        # Get suggestions
        suggestions = await audio_command_processor.get_command_suggestions(
            partial_command=request.partial_command,
            context=context
        )
        
        return {
            "success": True,
            "suggestions": suggestions
        }
        
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@app.post("/api/audio/command/validate")
async def validate_command_parameters(request: CommandValidationRequest):
    """Validate command parameters before execution"""
    try:
        # Get file path if provided
        input_file = None
        context = request.context.copy()
        if request.file_id:
            file_info = file_upload_service.get_file_info(request.file_id)
            if file_info and file_info.get('success'):
                input_file = file_info['file_path']
                context['file_info'] = file_info
        
        # Validate command
        validation_result = await audio_command_processor.validate_command_before_execution(
            command_text=request.command,
            input_file=input_file,
            context=context
        )
        
        return {
            "success": True,
            "validation": validation_result
        }
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to validate command: {str(e)}")

@app.get("/api/audio/command/stats")
async def get_command_processing_stats():
    """Get statistics about command processing capabilities"""
    try:
        stats = await audio_command_processor.get_processing_stats()
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# --- Direct Audio Editing Endpoints ---
@app.post("/api/audio/execute-command")
async def execute_direct_audio_command(request: AudioEditRequest):
    """Execute direct audio editing command (for testing)"""
    try:
        if not os.path.exists(request.input_file):
            raise HTTPException(status_code=404, detail="Input file not found")
        
        # Route to appropriate service based on operation
        if hasattr(advanced_audio_editing_service, request.operation):
            service_method = getattr(advanced_audio_editing_service, request.operation)
            result = await service_method(request.input_file, **request.params)
        elif hasattr(audio_editing_service, request.operation):
            service_method = getattr(audio_editing_service, request.operation)
            result = await service_method(request.input_file, **request.params)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown operation: {request.operation}")
        
        return result
        
    except Exception as e:
        logger.error(f"Direct command error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to execute operation: {str(e)}")

# --- LLM Endpoints ---
@app.get("/api/llm/providers")
async def get_llm_providers():
    """Get available LLM providers"""
    try:
        providers = llm_service.get_all_providers()
        # Convert to dict for JSON serialization
        providers_data = []
        for provider in providers:
            providers_data.append({
                "name": provider.name,
                "api_base_url": provider.api_base_url,
                "status": provider.status.value if hasattr(provider.status, 'value') else str(provider.status),
                "is_active": provider.is_active
            })
        
        return {
            "success": True,
            "providers": providers_data
        }
    except Exception as e:
        logger.error(f"LLM providers error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/llm/active-model")
async def get_active_model():
    """Get currently active LLM model"""
    try:
        active_model = llm_service.get_active_model()
        if active_model:
            model_data = {
                "model_id": active_model.model_id,
                "name": active_model.name,
                "provider_name": active_model.provider_name,
                "is_active": active_model.is_active,
                "capabilities": [cap.value if hasattr(cap, 'value') else str(cap) for cap in active_model.capabilities] if active_model.capabilities else []
            }
        else:
            model_data = None
            
        return {
            "success": True,
            "active_model": model_data
        }
    except Exception as e:
        logger.error(f"Active model error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/llm/set-model")
async def set_active_model(request: dict):
    """Set active LLM model"""
    try:
        model_name = request.get("model_name")
        if not model_name:
            raise HTTPException(status_code=400, detail="model_name is required")
        
        result = llm_service.set_active_model(model_name)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        logger.error(f"Set model error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Command Help Endpoints ---
@app.get("/api/audio/command/help")
async def get_command_help(command_type: Optional[str] = None):
    """Get help information for commands"""
    try:
        if command_type:
            try:
                command_enum = audio_command_processor.CommandType(command_type.upper())
                command_info = audio_command_processor.get_command_info(command_enum)
                return {
                    "success": True,
                    "command_info": command_info
                }
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Unknown command type: {command_type}")
        else:
            # Get all commands info
            commands_info = audio_command_processor.get_supported_commands_info()
            return {
                "success": True,
                "commands_info": commands_info
            }
        
    except Exception as e:
        logger.error(f"Help error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get command help: {str(e)}")

# --- Static Files ---
# Serve uploaded files (for development only)
if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# --- Error Handlers ---
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# --- Main Execution ---
if __name__ == "__main__":
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    # Run the server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=5000,
        reload=False,
        log_level="info"
    )