import sys
import os
import asyncio

# Add the parent directory (backend) to sys.path for module discovery
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from typing import Optional, List, Dict, Any
import asyncio
import time
from datetime import datetime
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from backend.services.ai.chat_security_service import security_service
from backend.api.schemas import (
    SendMessageRequest,
    SessionCreateRequest,
    SessionUpdateRequest,
    MessageCreateRequest,
    ExportSessionRequest,
)

from backend.models.chat import SessionNotFoundError, ModelNotAvailableError


def initialize_services():
    """
    Initialize all backend services with lazy loading
    אתחול כל שירותי הבקאנד עם טעינה עצלה
    """
    services = {}
    
    try:
        # Import services inside the function for lazy loading
        from backend.services.storage.file_upload import FileUploadService
        from backend.services.audio.metadata import AudioMetadataService
        from backend.services.audio.editing import AudioEditingService
        from backend.services.ai.session_service import SessionService
        from backend.services.ai.chat_history_service import ChatHistoryService
        from backend.services.ai.chat_service import ChatService
        
        # Try to initialize services one by one
        services['file_upload_service'] = FileUploadService()
        print("✅ File upload service initialized")
        
        services['audio_metadata_service'] = AudioMetadataService()
        print("✅ Audio metadata service initialized")
        
        services['audio_editing_service'] = AudioEditingService()
        print("✅ Audio editing service initialized")
        
        # LLM service might have issues with transformers, so we'll try it last
        try:
            from backend.services.ai.llm_service import LLMService
            services['llm_service'] = LLMService()
            print("✅ LLM service initialized")
        except Exception as e:
            print(f"⚠️ LLM service failed to initialize: {e}")
            services['llm_service'] = None

        # Chat-related services
        try:
            from backend.services.ai.session_service import SessionService
            from backend.services.ai.chat_history_service import ChatHistoryService
            from backend.services.ai.chat_service import ChatService

            services['session_service'] = SessionService()
            services['chat_history_service'] = ChatHistoryService()

            if services['llm_service']:
                services['chat_service'] = ChatService(
                    llm_service=services['llm_service'],
                    session_service=services['session_service'],
                    history_service=services['chat_history_service'],
                )
                print("✅ Chat service initialized")
            else:
                services['chat_service'] = None
                print("⚠️ Chat service skipped (LLM service unavailable)")
        except Exception as e:
            print(f"⚠️ Chat service failed to initialize: {e}")
            services['chat_service'] = None
        
        # Command processor depends on other services
        try:
            if services['llm_service']:
                from backend.services.ai.command_processor import AudioCommandProcessor
                services['audio_command_processor'] = AudioCommandProcessor(
                    llm_service=services['llm_service'],
                    audio_editing_service=services['audio_editing_service'],
                    audio_metadata_service=services['audio_metadata_service']
                )
                print("✅ Audio command processor initialized")
            else:
                services['audio_command_processor'] = None
                print("⚠️ Audio command processor skipped (LLM service unavailable)")
        except Exception as e:
            print(f"⚠️ Audio command processor failed to initialize: {e}")
            services['audio_command_processor'] = None
            
    except Exception as e:
        print(f"❌ Critical error during service initialization: {e}")
        raise
    
    return services

def configure_middleware(app: FastAPI) -> None:
    """
    Configure FastAPI middleware
    הגדרת middleware לאפליקציית FastAPI
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    יצירת והגדרת אפליקציית FastAPI
    """
    app = FastAPI(
        title="Audio Chat Studio API",
        description="Backend API for Audio Chat Studio",
        version="1.0.0"
    )
    
    # Configure middleware
    configure_middleware(app)
    
    return app

# --- Initialize Services ---
services = initialize_services()
llm_service = services['llm_service']
audio_editing_service = services['audio_editing_service']
file_upload_service = services['file_upload_service']
audio_metadata_service = services['audio_metadata_service']
audio_command_processor = services['audio_command_processor']
session_service = services['session_service']
chat_history_service = services['chat_history_service']
chat_service = services['chat_service']


# --- FastAPI App Initialization ---
app = create_app()
limiter = security_service.limiter
security_service.set_session_service(session_service)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- API Endpoints ---

@app.get('/')
async def read_root():
    return {"status": "ok", "message": "Audio Chat Python Backend is running!"}

@app.get('/health')
async def health_check():
    """Health check endpoint for monitoring"""
    active_model = None
    if llm_service:
        active_model_obj = llm_service.get_active_model()
        if active_model_obj:
            active_model = {
                "name": active_model_obj.name,
                "provider": active_model_obj.provider,
                "is_gemma": active_model_obj.provider == "Local Gemma"
            }
    
    return {
        "status": "healthy",
        "message": "Audio Chat Studio Backend is running",
        "active_model": active_model,
        "services": {
            "file_upload": file_upload_service is not None,
            "audio_metadata": audio_metadata_service is not None,
            "audio_editing": audio_editing_service is not None,
            "llm": llm_service is not None,
            "command_processor": audio_command_processor is not None
        }
    }

@app.post('/api/files/list')
async def list_files_endpoint(request: Request):
    data = await request.json()
    path = data.get('path', '.')
    pattern = data.get('pattern', '**/*')
    recursive = data.get('recursive', True)

    try:
        import glob
        files = [os.path.abspath(f) for f in glob.glob(os.path.join(path, pattern), recursive=recursive)]
        return JSONResponse(content=files)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/audio/upload')
async def upload_audio_file(file: UploadFile = File(...)):
    try:
        file_data = await file.read()
        original_filename = file.filename
        
        result = file_upload_service.upload_file(file_data, original_filename)
        
        if result["success"]:
            return JSONResponse(content={
                "success": True,
                "message": "File uploaded successfully",
                "file_id": result["file_id"],
                "original_filename": result["original_filename"],
                "stored_filename": result["stored_filename"],
                "file_size": result["file_size"],
                "metadata": result["metadata"],
                "validation": result["validation"]
            })
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get('/api/audio/files')
async def list_uploaded_files():
    try:
        files = file_upload_service.get_uploaded_files()
        return JSONResponse(content={
            "success": True,
            "files": files,
            "count": len(files)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.delete('/api/audio/files/{file_id}')
async def delete_uploaded_file(file_id: str):
    try:
        result = file_upload_service.delete_uploaded_file(file_id)
        
        if result["success"]:
            return JSONResponse(content={
                "success": True,
                "message": result["message"]
            })
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@app.get('/api/audio/metadata/{file_id}')
async def get_file_metadata(file_id: str):
    try:
        files = file_upload_service.get_uploaded_files()
        target_file = None
        
        for file_info in files:
            if file_id in file_info["filename"]:
                target_file = file_info
                break
        
        if not target_file:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
        
        metadata_result = file_upload_service.extract_metadata(target_file["file_path"])
        
        if metadata_result["success"]:
            return JSONResponse(content={
                "success": True,
                "file_info": target_file,
                "metadata": metadata_result["metadata"]
            })
        else:
            raise HTTPException(status_code=500, detail=metadata_result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metadata: {str(e)}")

@app.get('/api/audio/metadata/advanced/{file_id}')
async def get_advanced_metadata(file_id: str, include_advanced: bool = True):
    try:
        files = file_upload_service.get_uploaded_files()
        target_file = None
        
        for file_info in files:
            if file_id in file_info["filename"]:
                target_file = file_info
                break
        
        if not target_file:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
        
        metadata = audio_metadata_service.extract_comprehensive_metadata(
            target_file["file_path"], 
            include_advanced=include_advanced
        )
        
        return JSONResponse(content=metadata)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract advanced metadata: {str(e)}")

@app.get('/api/audio/summary/{file_id}')
async def get_audio_summary(file_id: str):
    try:
        files = file_upload_service.get_uploaded_files()
        target_file = None
        
        for file_info in files:
            if file_id in file_info["filename"]:
                target_file = file_info
                break
        
        if not target_file:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
        
        summary = audio_metadata_service.get_audio_summary(target_file["file_path"])
        
        return JSONResponse(content=summary)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate audio summary: {str(e)}")

@app.get('/api/audio/waveform/{file_id}')
async def get_waveform_data(file_id: str, max_points: int = 1000):
    try:
        files = file_upload_service.get_uploaded_files()
        target_file = None
        
        for file_info in files:
            if file_id in file_info["filename"]:
                target_file = file_info
                break
        
        if not target_file:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
        
        waveform_data = audio_metadata_service.extract_waveform_data(
            target_file["file_path"], 
            max_points=max_points
        )
        
        return JSONResponse(content=waveform_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract waveform data: {str(e)}")

@app.get('/api/audio/spectrogram/{file_id}')
async def get_spectrogram_data(file_id: str, n_fft: int = 2048, hop_length: int = 512):
    try:
        files = file_upload_service.get_uploaded_files()
        target_file = None
        
        for file_info in files:
            if file_id in file_info["filename"]:
                target_file = file_info
                break
        
        if not target_file:
            raise HTTPException(status_code=404, detail=f"File with ID {file_id} not found")
        
        spectrogram_data = audio_metadata_service.extract_spectrogram_data(
            target_file["file_path"], 
            n_fft=n_fft,
            hop_length=hop_length
        )
        
        return JSONResponse(content=spectrogram_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract spectrogram data: {str(e)}")

@app.post('/api/audio/metadata')
async def extract_audio_metadata(request: Request):
    try:
        data = await request.json()
        
        if not data:
            raise HTTPException(status_code=400, detail="Request body is required")
        
        file_path = data.get('file_path')
        file_id = data.get('file_id')
        include_advanced = data.get('include_advanced', True)
        analysis_type = data.get('analysis_type', 'full')
        
        if file_path:
            if not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
            target_path = file_path
            
        elif file_id:
            files = file_upload_service.get_uploaded_files()
            target_file = None
            
            for file_info in files:
                if file_id in file_info["filename"]:
                    target_file = file_info
                    break
            
            if not target_file:
                raise HTTPException(status_code=404, detail="File with ID {file_id} not found")
            
            target_path = target_file["file_path"]
            
        else:
            raise HTTPException(status_code=400, detail="Either 'file_path' or 'file_id' must be provided")
        
        if analysis_type == 'summary':
            result = audio_metadata_service.get_audio_summary(target_path)
        elif analysis_type == 'basic':
            result = audio_metadata_service.extract_comprehensive_metadata(
                target_path, 
                include_advanced=False
            )
        else:
            result = audio_metadata_service.extract_comprehensive_metadata(
                target_path, 
                include_advanced=include_advanced
            )
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract metadata: {str(e)}")

@app.post('/api/audio/transcribe')
async def transcribe_audio_endpoint(audio_base64: str = Form(...)):
    try:
        transcription = audio_editing_service.transcribe_audio(audio_base64)
        return JSONResponse(content={"transcription": transcription})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/audio/process-command')
async def process_audio_command(command: str = Form(...), filename: str = Form(...)):
    try:
        response = audio_editing_service.process_natural_language_command(command, filename)
        return JSONResponse(content={
            "response": response.get("message", "Command processed successfully"),
            "status": response.get("status", "completed"),
            "processed_file": response.get("processed_file"),
            "details": response.get("details")
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process command: {str(e)}")

@app.post('/api/audio/execute-command')
async def execute_audio_command(request: Request):
    try:
        data = await request.json()
        
        if not data:
            raise HTTPException(status_code=400, detail="Request body is required")
        
        command = data.get('command')
        filename = data.get('filename')
        file_id = data.get('file_id')
        
        if not command:
            raise HTTPException(status_code=400, detail="command is required")
        
        target_filename = filename
        target_file_path = None
        
        if file_id:
            files = file_upload_service.get_uploaded_files()
            target_file = None
            
            for file_info in files:
                if file_id in file_info["filename"]:
                    target_file = file_info
                    break
            
            if not target_file:
                raise HTTPException(status_code=404, detail="File with ID {file_id} not found")
            
            target_filename = target_file["original_filename"]
            target_file_path = target_file["file_path"]
        
        elif not filename:
            raise HTTPException(status_code=400, detail="Either 'filename' or 'file_id' must be provided")
        
        response = audio_editing_service.process_natural_language_command(command, target_filename)
        
        if target_file_path:
            response["source_file_path"] = target_file_path
        
        return JSONResponse(content={
            "success": response.get("status") == "completed",
            "command": command,
            "target_file": target_filename,
            "message": response.get("message"),
            "processed_file": response.get("processed_file"),
            "details": response.get("details"),
            "status": response.get("status")
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")

@app.get('/api/llm/providers')
async def get_all_providers():
    try:
        if llm_service is None:
            raise HTTPException(status_code=503, detail="LLM service is not available")
        providers = llm_service.get_all_providers()
        provider_list = [p.to_dict() for p in providers]
        return JSONResponse(content=provider_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve providers: {e}")

@app.get('/api/llm/models')
async def get_all_models(provider: Optional[str] = None):
    try:
        if llm_service is None:
            raise HTTPException(status_code=503, detail="LLM service is not available")
        if provider:
            models = llm_service.get_models_by_provider(provider)
        else:
            models = llm_service.get_all_models()
        model_list = [m.to_dict() for m in models]
        return JSONResponse(content=model_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve models: {e}")

@app.get('/api/llm/active-model')
async def get_active_model():
    try:
        if llm_service is None:
            raise HTTPException(status_code=503, detail="LLM service is not available")
        active_model = llm_service.get_active_model()
        if active_model:
            return JSONResponse(content=active_model.to_dict())
        else:
            return JSONResponse(content=None)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve active model: {e}")

@app.post('/api/llm/active-model')
async def set_active_model(model_id: str = Form(...)):
    try:
        if llm_service is None:
            raise HTTPException(status_code=503, detail="LLM service is not available")
        success = llm_service.set_active_model(model_id)
        return JSONResponse(content={"success": success})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set active model: {e}")

@app.post('/api/llm/test-chat')
async def test_chat(request: Request):
    """Test chat with the active model"""
    try:
        if llm_service is None:
            raise HTTPException(status_code=503, detail="LLM service is not available")
        
        data = await request.json()
        message = data.get('message', 'Hello')
        
        # Get active model
        active_model = llm_service.get_active_model()
        if not active_model:
            raise HTTPException(status_code=400, detail="No active model set")
        
        # Generate response
        messages = [{"role": "user", "content": message}]
        response = llm_service.generate_chat_response(messages)
        
        if response and response.success:
            return JSONResponse(content={
                "success": True,
                "response": response.content,
                "model": active_model.name
            })
        else:
            return JSONResponse(content={
                "success": False,
                "error": response.error_message if response else "Unknown error"
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test chat: {e}")


@app.post('/api/llm/set-api-key')
async def set_provider_api_key(request: Request):
    """Set the API key for an LLM provider"""
    try:
        if llm_service is None:
            raise HTTPException(status_code=503, detail="LLM service is not available")

        data = await request.json()
        provider_name = data.get('provider_name')
        api_key = data.get('api_key')

        if not provider_name or not api_key:
            raise HTTPException(status_code=400, detail="provider_name and api_key are required")

        success = llm_service.set_provider_api_key(provider_name, api_key)

        if success:
            return JSONResponse(content={"success": True, "message": "API key saved"})
        else:
            return JSONResponse(content={"success": False, "error": "Failed to save API key"})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set API key: {e}")


@app.post('/api/llm/test-connection')
async def test_provider_connection(request: Request):
    """Test connection for a specific LLM provider"""
    try:
        if llm_service is None:
            raise HTTPException(status_code=503, detail="LLM service is not available")

        data = await request.json()
        provider_name = data.get('provider_name')

        if not provider_name:
            raise HTTPException(status_code=400, detail="provider_name is required")

        success = llm_service.test_provider_connection(provider_name)
        provider = llm_service.get_provider(provider_name)
        message = provider.error_message if provider and provider.error_message else "Connection successful"

        return JSONResponse(content={"success": success, "message": message})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test connection: {e}")

@app.post('/api/llm/chat')
async def chat_endpoint(request: Request):
    """Simple chat endpoint for general conversation"""
    try:
        if llm_service is None:
            raise HTTPException(status_code=503, detail="LLM service is not available")
        
        data = await request.json()
        messages = data.get('messages', [])
        
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        # Generate response using the active model
        response = llm_service.generate_chat_response(messages)
        
        if response and response.success:
            return JSONResponse(content={
                "success": True,
                "content": response.content,
                "model_id": response.model_id,
                "usage": response.usage
            })
        else:
            error_msg = response.error_message if response else "Unknown error"
            return JSONResponse(content={
                "success": False,
                "content": "מצטער, לא הצלחתי לענות על השאלה. אנא נסה שוב.",
                "error": error_msg
            })
            
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "content": "מצטער, אירעה שגיאה טכנית. אנא נסה שוב.",
            "error": str(e)
        })

@app.post('/api/llm/chat/completion')
async def chat_completion_endpoint(messages: List[Dict[str, str]]):
    try:
        if llm_service is None:
            raise HTTPException(status_code=503, detail="LLM service is not available")
        response = llm_service.generate_chat_response(messages)
        if response:
            return JSONResponse(content=response.to_dict())
        else:
            raise HTTPException(status_code=500, detail="Failed to get response from LLM")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/chat/send')
@limiter.limit("5/minute")
async def send_chat_message(payload: SendMessageRequest, request: Request):
    """Send a chat message and return the response"""
    if chat_service is None:
        raise HTTPException(status_code=503, detail="Chat service is not available")
    
    start_time = time.time()
    success = False
    error_message = None
    
    try:
        # Sanitize user input
        sanitized_message = security_service.sanitize_input(payload.message)
        
        # Validate session access
        if payload.user_id:
            if not security_service.validate_session_access(payload.session_id, payload.user_id):
                raise HTTPException(status_code=403, detail="Access to this session is forbidden")

        result = chat_service.send_message(payload.session_id, sanitized_message, payload.user_id)
        success = True
        
        # Log audit event
        try:
            from backend.services.security.audit_service import log_api_request
            log_api_request(
                action="POST /api/chat/send",
                user_id=payload.user_id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                duration_ms=int((time.time() - start_time) * 1000),
                success=True
            )
        except Exception as audit_error:
            logger.warning(f"Failed to log audit event: {audit_error}")
        
        return JSONResponse(content=result.to_dict())
    except SessionNotFoundError as e:
        error_message = str(e)
        raise HTTPException(status_code=404, detail=str(e))
    except ModelNotAvailableError as e:
        error_message = str(e)
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        error_message = str(e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Log audit event for errors
        if not success and error_message:
            try:
                from backend.services.security.audit_service import log_api_request
                log_api_request(
                    action="POST /api/chat/send",
                    user_id=payload.user_id,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    duration_ms=int((time.time() - start_time) * 1000),
                    success=False,
                    error_message=error_message
                )
            except Exception as audit_error:
                logger.warning(f"Failed to log audit event: {audit_error}")


@app.post('/api/chat/stream')
@limiter.limit("5/minute")
async def stream_chat_message(payload: SendMessageRequest, request: Request):
    """Stream chat response using Server-Sent Events"""
    if chat_service is None:
        raise HTTPException(status_code=503, detail="Chat service is not available")

    # Sanitize user input
    sanitized_message = security_service.sanitize_input(payload.message)

    # Validate session access
    if payload.user_id:
        if not security_service.validate_session_access(payload.session_id, payload.user_id):
            raise HTTPException(status_code=403, detail="Access to this session is forbidden")

    async def event_generator():
        try:
            async for chunk in chat_service.stream_message(payload.session_id, sanitized_message, payload.user_id, request=request):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except SessionNotFoundError as e:
            yield f"event: error\ndata: {str(e)}\n\n"
        except ModelNotAvailableError as e:
            yield f"event: error\ndata: {str(e)}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n"

    return StreamingResponse(event_generator(), media_type='text/event-stream')




@app.get('/api/chat/sessions')
async def list_chat_sessions(user_id: Optional[str] = None):
    if session_service is None:
        raise HTTPException(status_code=503, detail="Session service is not available")
    sessions = session_service.list_user_sessions(user_id=user_id)
    return [s.to_dict() for s in sessions]


@app.post('/api/chat/sessions')
async def create_chat_session(request: SessionCreateRequest):
    if session_service is None:
        raise HTTPException(status_code=503, detail="Session service is not available")
    session = session_service.create_session(title=request.title, model_id=request.model_id, user_id=request.user_id)
    return session.to_dict()


@app.get('/api/chat/sessions/{session_id}')
async def get_chat_session(session_id: str):
    if session_service is None:
        raise HTTPException(status_code=503, detail="Session service is not available")
    session = session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.to_dict()


@app.put('/api/chat/sessions/{session_id}')
async def update_chat_session(session_id: str, request: SessionUpdateRequest):
    if session_service is None:
        raise HTTPException(status_code=503, detail="Session service is not available")
    updates = {k: v for k, v in request.dict(exclude_unset=True).items()}
    success = session_service.update_session(session_id, **updates)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True}


@app.delete('/api/chat/sessions/{session_id}')
async def delete_chat_session(session_id: str):
    if session_service is None:
        raise HTTPException(status_code=503, detail="Session service is not available")
    success = session_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True}


@app.get('/api/chat/sessions/{session_id}/messages')
async def get_session_messages(session_id: str, limit: Optional[int] = None, offset: int = 0):
    if chat_history_service is None:
        raise HTTPException(status_code=503, detail="Chat history service is not available")
    messages = chat_history_service.get_session_messages(session_id, limit=limit, offset=offset)
    return [m.to_dict() for m in messages]


@app.post('/api/chat/sessions/{session_id}/messages')
async def create_session_message(session_id: str, request: MessageCreateRequest):
    if chat_history_service is None:
        raise HTTPException(status_code=503, detail="Chat history service is not available")
    
    from backend.models.chat import Message
    from datetime import datetime
    
    message = Message(
        id="",
        session_id=session_id,
        role=request.role,
        content=request.content,
        timestamp=datetime.utcnow(),
        model_id=request.model_id,
        tokens_used=request.tokens_used,
        response_time=request.response_time,
        metadata=request.metadata or {}
    )
    
    message_id = chat_history_service.save_message(session_id, message)
    return {"message_id": message_id, "success": True}


@app.get('/api/chat/search')
async def search_messages(query: str, user_id: Optional[str] = None, session_id: Optional[str] = None):
    if chat_history_service is None:
        raise HTTPException(status_code=503, detail="Chat history service is not available")
    messages = chat_history_service.search_messages(query, user_id=user_id, session_id=session_id)
    return [m.to_dict() for m in messages]


@app.post('/api/chat/export/{session_id}')
async def export_session(session_id: str, request: ExportSessionRequest):
    if chat_history_service is None:
        raise HTTPException(status_code=503, detail="Chat history service is not available")
    
    try:
        exported_data = chat_history_service.export_session(session_id, format=request.format)
        
        # Set appropriate content type based on format
        if request.format == "json":
            media_type = "application/json"
            filename = f"session_{session_id}.json"
        elif request.format == "markdown":
            media_type = "text/markdown"
            filename = f"session_{session_id}.md"
        else:  # txt
            media_type = "text/plain"
            filename = f"session_{session_id}.txt"
        
        return Response(
            content=exported_data,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Security and Encryption Endpoints ---

@app.get('/api/security/encryption/status')
async def get_encryption_status():
    """Get current encryption status and key information"""
    try:
        if chat_history_service is None:
            raise HTTPException(status_code=503, detail="Chat history service is not available")
        
        status = chat_history_service.get_encryption_status()
        return JSONResponse(content=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get encryption status: {str(e)}")


@app.post('/api/security/encryption/rotate-keys')
async def rotate_encryption_keys():
    """Manually rotate encryption keys"""
    try:
        from backend.services.security.encryption_service import encryption_service
        
        new_key_id = encryption_service.rotate_keys()
        key_info = encryption_service.get_key_info()
        
        return JSONResponse(content={
            "success": True,
            "message": "Encryption keys rotated successfully",
            "new_key_id": new_key_id,
            "key_info": key_info
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rotate keys: {str(e)}")


@app.post('/api/security/encryption/migrate')
async def migrate_to_encryption():
    """Migrate existing unencrypted messages to encrypted format"""
    try:
        if chat_history_service is None:
            raise HTTPException(status_code=503, detail="Chat history service is not available")
        
        result = chat_history_service.migrate_to_encryption()
        
        return JSONResponse(content={
            "success": True,
            "message": "Migration completed",
            "migrated_count": result["migrated_count"],
            "failed_count": result["failed_count"],
            "total_messages": result["total_messages"]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to migrate to encryption: {str(e)}")


@app.post('/api/security/encryption/verify')
async def verify_encryption_integrity(session_id: Optional[str] = None):
    """Verify encryption integrity for messages"""
    try:
        if chat_history_service is None:
            raise HTTPException(status_code=503, detail="Chat history service is not available")
        
        result = chat_history_service.verify_message_encryption(session_id=session_id)
        
        return JSONResponse(content={
            "success": True,
            "verification_result": result
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify encryption: {str(e)}")


@app.post('/api/security/encryption/cleanup')
async def cleanup_old_keys(keep_days: int = 90):
    """Clean up old encryption keys"""
    try:
        from backend.services.security.encryption_service import encryption_service
        
        result = encryption_service.cleanup_old_keys(keep_days=keep_days)
        
        return JSONResponse(content={
            "success": True,
            "message": "Cleanup completed",
            "deleted_keys": result["deleted_keys"],
            "deleted_metadata": result["deleted_metadata"]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup keys: {str(e)}")


@app.get('/api/security/encryption/integrity')
async def check_encryption_integrity():
    """Check overall encryption system integrity"""
    try:
        from backend.services.security.encryption_service import encryption_service
        
        integrity = encryption_service.verify_encryption_integrity()
        
        return JSONResponse(content={
            "success": True,
            "integrity_check": integrity
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check integrity: {str(e)}")


# --- Audit Logging Endpoints ---

@app.get('/api/security/audit/events')
async def get_audit_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_types: Optional[str] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    severity: Optional[str] = None,
    success_only: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get audit events with filtering options"""
    try:
        from backend.services.security.audit_service import audit_service, AuditEventType, AuditSeverity
        
        # Parse parameters
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        event_type_list = None
        if event_types:
            try:
                event_type_list = [AuditEventType(et.strip()) for et in event_types.split(',')]
            except ValueError as e:
                raise HTTPException(status_code=400, detail=f"Invalid event type: {str(e)}")
        
        severity_enum = None
        if severity:
            try:
                severity_enum = AuditSeverity(severity)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        
        # Get events
        events = audit_service.get_events(
            start_date=start_dt,
            end_date=end_dt,
            event_types=event_type_list,
            user_id=user_id,
            session_id=session_id,
            severity=severity_enum,
            success_only=success_only,
            limit=limit,
            offset=offset
        )
        
        return JSONResponse(content={
            "success": True,
            "events": [event.to_dict() for event in events],
            "count": len(events)
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit events: {str(e)}")


@app.get('/api/security/audit/statistics')
async def get_audit_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """Get audit statistics"""
    try:
        from backend.services.security.audit_service import audit_service
        
        # Parse parameters
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        statistics = audit_service.get_statistics(
            start_date=start_dt,
            end_date=end_dt
        )
        
        return JSONResponse(content={
            "success": True,
            "statistics": statistics
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit statistics: {str(e)}")


@app.get('/api/security/audit/search')
async def search_audit_events(
    q: str,
    fields: Optional[str] = None
):
    """Search audit events"""
    try:
        from backend.services.security.audit_service import audit_service
        
        if not q or len(q.strip()) < 2:
            raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
        
        search_fields = None
        if fields:
            search_fields = [field.strip() for field in fields.split(',')]
        
        events = audit_service.search_events(
            search_term=q.strip(),
            search_fields=search_fields
        )
        
        return JSONResponse(content={
            "success": True,
            "events": [event.to_dict() for event in events],
            "count": len(events),
            "query": q
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search audit events: {str(e)}")


@app.post('/api/security/audit/verify')
async def verify_audit_integrity():
    """Verify audit log integrity"""
    try:
        from backend.services.security.audit_service import audit_service
        
        integrity = audit_service.verify_integrity()
        
        return JSONResponse(content={
            "success": True,
            "integrity_check": integrity
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify audit integrity: {str(e)}")


@app.post('/api/security/audit/cleanup')
async def cleanup_audit_logs(retention_days: int = 365):
    """Clean up old audit logs"""
    try:
        from backend.services.security.audit_service import audit_service
        
        if retention_days < 1 or retention_days > 3650:  # 1 day to 10 years
            raise HTTPException(status_code=400, detail="Retention days must be between 1 and 3650")
        
        result = audit_service.cleanup_old_logs(retention_days=retention_days)
        
        return JSONResponse(content={
            "success": True,
            "message": "Audit logs cleaned up successfully",
            "deleted_events": result["deleted_events"],
            "deleted_statistics": result["deleted_statistics"]
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup audit logs: {str(e)}")


@app.get('/api/security/audit/export')
async def export_audit_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    format: str = "json"
):
    """Export audit logs"""
    try:
        from backend.services.security.audit_service import audit_service
        
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
        
        # Parse parameters
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        exported_data = audit_service.export_logs(
            start_date=start_dt,
            end_date=end_dt,
            format=format
        )
        
        # Set appropriate content type and filename
        if format == "json":
            media_type = "application/json"
            filename = f"audit-logs-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
        else:  # csv
            media_type = "text/csv"
            filename = f"audit-logs-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.csv"
        
        return Response(
            content=exported_data,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export audit logs: {str(e)}")


@app.post('/api/security/audit/log')
async def log_audit_event(request: Request):
    """Manually log an audit event (for testing or special cases)"""
    try:
        from backend.services.security.audit_service import audit_service, AuditEventType, AuditSeverity
        
        data = await request.json()
        
        # Validate required fields
        if not data.get('event_type') or not data.get('action'):
            raise HTTPException(status_code=400, detail="event_type and action are required")
        
        try:
            event_type = AuditEventType(data['event_type'])
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid event_type: {data['event_type']}")
        
        severity = AuditSeverity.LOW
        if data.get('severity'):
            try:
                severity = AuditSeverity(data['severity'])
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {data['severity']}")
        
        # Log the event
        event_id = audit_service.log_event(
            event_type=event_type,
            action=data['action'],
            user_id=data.get('user_id'),
            session_id=data.get('session_id'),
            resource=data.get('resource'),
            details=data.get('details', {}),
            severity=severity,
            success=data.get('success', True),
            error_message=data.get('error_message'),
            duration_ms=data.get('duration_ms'),
            ip_address=data.get('ip_address'),
            user_agent=data.get('user_agent')
        )
        
        return JSONResponse(content={
            "success": True,
            "message": "Audit event logged successfully",
            "event_id": event_id
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log audit event: {str(e)}")


# --- Data Management and Privacy Endpoints ---

@app.get('/api/data/statistics')
async def get_data_statistics():
    """Get data usage statistics for privacy dashboard"""
    try:
        if chat_history_service is None or session_service is None:
            raise HTTPException(status_code=503, detail="Required services are not available")
        
        # Get session statistics
        sessions = session_service.list_user_sessions()
        total_sessions = len(sessions)
        
        # Get message statistics
        total_messages = 0
        encrypted_messages = 0
        oldest_data = None
        storage_used = 0
        
        for session in sessions:
            session_stats = chat_history_service.get_session_statistics(session.id)
            total_messages += session_stats["message_counts"]["total"]
            
            # Estimate storage (rough calculation)
            storage_used += session_stats["message_counts"]["total"] * 500  # ~500 bytes per message
            
            # Check oldest data
            if session_stats["date_range"]["first_message"]:
                if not oldest_data or session_stats["date_range"]["first_message"] < oldest_data:
                    oldest_data = session_stats["date_range"]["first_message"]
        
        # Try to get encryption statistics
        try:
            encryption_status = chat_history_service.get_encryption_status()
            if encryption_status.get("encryption_enabled", False):
                encrypted_messages = total_messages  # Assume all are encrypted if encryption is enabled
        except:
            pass
        
        return JSONResponse(content={
            "totalMessages": total_messages,
            "totalSessions": total_sessions,
            "storageUsed": storage_used,
            "oldestData": oldest_data,
            "encryptedMessages": encrypted_messages
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get data statistics: {str(e)}")


@app.post('/api/data/clear-all')
async def clear_all_data():
    """Clear all chat data (sessions and messages)"""
    try:
        if chat_history_service is None or session_service is None:
            raise HTTPException(status_code=503, detail="Required services are not available")
        
        # Get all sessions
        sessions = session_service.list_user_sessions()
        
        deleted_messages = 0
        deleted_sessions = 0
        
        # Delete all messages and sessions
        for session in sessions:
            message_count = chat_history_service.delete_session_messages(session.id)
            deleted_messages += message_count
            
            if session_service.delete_session(session.id):
                deleted_sessions += 1
        
        # Log security event
        try:
            from backend.services.security.audit_service import log_security_event, AuditSeverity
            log_security_event(
                action="all_data_cleared",
                severity=AuditSeverity.CRITICAL,
                details={
                    "deleted_messages": deleted_messages,
                    "deleted_sessions": deleted_sessions,
                    "total_sessions": len(sessions)
                }
            )
        except Exception as audit_error:
            logger.warning(f"Failed to log audit event: {audit_error}")
        
        return JSONResponse(content={
            "success": True,
            "message": "All data cleared successfully",
            "deleted_messages": deleted_messages,
            "deleted_sessions": deleted_sessions
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear data: {str(e)}")


@app.get('/api/data/export')
async def export_all_data():
    """Export all chat data for backup"""
    try:
        if chat_history_service is None or session_service is None:
            raise HTTPException(status_code=503, detail="Required services are not available")
        
        # Get all sessions
        sessions = session_service.list_user_sessions()
        
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "sessions": [],
            "encryption_status": None
        }
        
        # Add encryption status
        try:
            export_data["encryption_status"] = chat_history_service.get_encryption_status()
        except:
            pass
        
        # Export each session
        for session in sessions:
            session_data = session.to_dict()
            
            # Get messages for this session
            messages = chat_history_service.get_session_messages(session.id)
            session_data["messages"] = [m.to_dict() for m in messages]
            
            # Get session statistics
            try:
                session_data["statistics"] = chat_history_service.get_session_statistics(session.id)
            except:
                pass
            
            export_data["sessions"].append(session_data)
        
        # Convert to JSON
        import json
        json_data = json.dumps(export_data, ensure_ascii=False, indent=2)
        
        # Log security event
        try:
            from backend.services.security.audit_service import log_security_event, AuditSeverity
            log_security_event(
                action="data_exported",
                severity=AuditSeverity.HIGH,
                details={
                    "exported_sessions": len(export_data["sessions"]),
                    "export_format": "json",
                    "data_size_bytes": len(json_data),
                    "includes_encryption_status": export_data["encryption_status"] is not None
                }
            )
        except Exception as audit_error:
            logger.warning(f"Failed to log audit event: {audit_error}")
        
        return Response(
            content=json_data,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=chat-data-export-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export data: {str(e)}")


# --- Settings Endpoints ---

@app.get('/api/settings/privacy')
async def get_privacy_settings():
    """Get current privacy settings"""
    try:
        # For now, return default settings
        # In a real implementation, these would be stored in a database or config file
        default_settings = {
            "localOnlyMode": False,
            "dataRetentionDays": 90,
            "encryptionEnabled": True,
            "anonymousMode": False,
            "telemetryEnabled": True,
            "crashReportsEnabled": True,
            "usageAnalyticsEnabled": False,
            "autoDeleteEnabled": False,
            "backupEnabled": True,
            "cloudSyncEnabled": False
        }
        
        return JSONResponse(content=default_settings)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get privacy settings: {str(e)}")


@app.post('/api/settings/privacy')
async def save_privacy_settings(request: Request):
    """Save privacy settings"""
    try:
        settings = await request.json()
        
        # In a real implementation, these would be saved to a database or config file
        # For now, we'll just validate and return success
        
        required_fields = [
            "localOnlyMode", "dataRetentionDays", "encryptionEnabled", 
            "anonymousMode", "telemetryEnabled", "crashReportsEnabled",
            "usageAnalyticsEnabled", "autoDeleteEnabled", "backupEnabled", "cloudSyncEnabled"
        ]
        
        for field in required_fields:
            if field not in settings:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate data types
        if not isinstance(settings["dataRetentionDays"], int) or settings["dataRetentionDays"] < 1:
            raise HTTPException(status_code=400, detail="dataRetentionDays must be a positive integer")
        
        return JSONResponse(content={
            "success": True,
            "message": "Privacy settings saved successfully"
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save privacy settings: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)sion_id}')
async def delete_chat_session(session_id: str):
    if session_service is None:
        raise HTTPException(status_code=503, detail="Session service is not available")
    success = session_service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True}


# Message Management Endpoints

@app.get('/api/chat/sessions/{session_id}/messages')
async def get_session_messages(session_id: str, limit: Optional[int] = None, offset: int = 0):
    """Get messages for a specific session"""
    if chat_history_service is None:
        raise HTTPException(status_code=503, detail="Chat history service is not available")
    
    # Verify session exists
    if session_service:
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        messages = chat_history_service.get_session_messages(session_id, limit=limit, offset=offset)
        return [msg.to_dict() for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get messages: {str(e)}")


@app.post('/api/chat/sessions/{session_id}/messages')
async def add_message_to_session(session_id: str, request: MessageCreateRequest):
    """Add a message to a session (for importing or manual entry)"""
    if chat_history_service is None:
        raise HTTPException(status_code=503, detail="Chat history service is not available")
    
    # Verify session exists
    if session_service:
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        if not request.content:
            raise HTTPException(status_code=400, detail="Message content is required")
        
        if request.role not in ['user', 'assistant', 'system']:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 'user', 'assistant', or 'system'")
        
        from backend.models.chat import Message
        from datetime import datetime
        import uuid
        
        message = Message(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=request.role,
            content=request.content,
            timestamp=datetime.utcnow(),
            model_id=request.model_id,
            tokens_used=request.tokens_used,
            response_time=request.response_time,
            metadata=request.metadata or {}
        )
        
        message_id = chat_history_service.save_message(session_id, message)
        
        # Update session message count
        if session_service:
            session_service.increment_message_count(session_id, 1)
        
        return {"success": True, "message_id": message_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


@app.get('/api/chat/search')
async def search_messages(query: str, user_id: Optional[str] = None, session_id: Optional[str] = None, limit: int = 50):
    """Search messages across sessions"""
    if chat_history_service is None:
        raise HTTPException(status_code=503, detail="Chat history service is not available")
    
    if not query or len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Search query must be at least 2 characters")
    
    try:
        messages = chat_history_service.search_messages(query, user_id=user_id, session_id=session_id)
        return [msg.to_dict() for msg in messages[:limit]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search messages: {str(e)}")


@app.post('/api/chat/export/{session_id}')
async def export_session(session_id: str, request: ExportSessionRequest):
    """Export session messages in various formats"""
    if chat_history_service is None:
        raise HTTPException(status_code=503, detail="Chat history service is not available")
    
    # Verify session exists
    if session_service:
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        format_type = request.format.lower()
        
        if format_type not in ['json', 'markdown', 'txt']:
            raise HTTPException(status_code=400, detail="Invalid format. Must be 'json', 'markdown', or 'txt'")
        
        exported_data = chat_history_service.export_session(session_id, format=format_type)
        
        # Set appropriate content type
        content_types = {
            'json': 'application/json',
            'markdown': 'text/markdown',
            'txt': 'text/plain'
        }
        
        return Response(
            content=exported_data,
            media_type=content_types[format_type],
            headers={
                "Content-Disposition": f"attachment; filename=session_{session_id}.{format_type}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export session: {str(e)}")

@app.post('/api/audio/command/interpret')
async def interpret_audio_command(request: Request):
    try:
        if audio_command_processor is None:
            raise HTTPException(status_code=503, detail="Audio command processor is not available")
            
        data = await request.json()
        command_text = data.get('command')
        file_id = data.get('file_id')
        context = data.get('context', {})
        
        if not command_text:
            raise HTTPException(status_code=400, detail="command is required")
        
        input_file = None
        if file_id:
            file_info = file_upload_service.get_file_info(file_id)
            if file_info and file_info.get('success'):
                input_file = file_info['file_path']
            else:
                raise HTTPException(status_code=404, detail="File not found")
        
        validation_result = await audio_command_processor.validate_command_before_execution(
            command_text=command_text,
            input_file=input_file,
            context=context
        )
        
        return JSONResponse(content={
            "success": True,
            "interpretation": validation_result
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to interpret command: {str(e)}")

@app.post('/api/audio/command/execute')
async def execute_audio_command_new(request: Request):
    try:
        if audio_command_processor is None:
            raise HTTPException(status_code=503, detail="Audio command processor is not available")
            
        data = await request.json()
        command_text = data.get('command')
        file_id = data.get('file_id')
        context = data.get('context', {})
        
        if not command_text:
            raise HTTPException(status_code=400, detail="command is required")
        
        if not file_id:
            raise HTTPException(status_code=400, detail="file_id is required")
        
        file_info = file_upload_service.get_file_info(file_id)
        if not file_info or not file_info.get('success'):
            raise HTTPException(status_code=404, detail="File not found")
        
        input_file = file_info['file_path']
        
        result = await audio_command_processor.process_command(
            command_text=command_text,
            input_file=input_file,
            context=context
        )
        
        response_data = audio_command_processor.to_dict(result)
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute command: {str(e)}")

@app.post('/api/audio/command/suggestions')
async def get_command_suggestions(request: Request):
    try:
        if audio_command_processor is None:
            raise HTTPException(status_code=503, detail="Audio command processor is not available")
            
        data = await request.json()
        partial_command = data.get('partial_command', '')
        file_id = data.get('file_id')
        context = data.get('context', {})
        
        if file_id:
            file_info = file_upload_service.get_file_info(file_id)
            if file_info and file_info.get('success'):
                context['file_info'] = file_info
        
        suggestions = await audio_command_processor.get_command_suggestions(
            partial_command=partial_command,
            context=context
        )
        
        return JSONResponse(content={
            "success": True,
            "suggestions": suggestions
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")

@app.get('/api/audio/command/help')
async def get_command_help(command_type: Optional[str] = None):
    try:
        if audio_command_processor is None:
            raise HTTPException(status_code=503, detail="Audio command processor is not available")
            
        if command_type:
            from backend.services.ai.command_interpreter import CommandType
            try:
                cmd_type = CommandType(command_type)
                help_info = audio_command_processor.interpreter.get_command_help(cmd_type)
                return JSONResponse(content={
                    "success": True,
                    "command_help": help_info
                })
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Unknown command type: {command_type}")
        else:
            commands_info = audio_command_processor.get_supported_commands_info()
            return JSONResponse(content={
                "success": True,
                "commands_info": commands_info
            })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get command help: {str(e)}")

@app.post('/api/audio/command/validate')
async def validate_command_parameters(request: Request):
    try:
        if audio_command_processor is None:
            raise HTTPException(status_code=503, detail="Audio command processor is not available")
            
        data = await request.json()
        command_text = data.get('command')
        file_id = data.get('file_id')
        context = data.get('context', {})
        
        if not command_text:
            raise HTTPException(status_code=400, detail="command is required")
        
        input_file = None
        if file_id:
            file_info = file_upload_service.get_file_info(file_id)
            if file_info and file_info.get('success'):
                input_file = file_info['file_path']
                context['file_info'] = file_info
        
        validation_result = await audio_command_processor.validate_command_before_execution(
            command_text=command_text,
            input_file=input_file,
            context=context
        )
        
        return JSONResponse(content={
            "success": True,
            "validation": validation_result
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate command: {str(e)}")

@app.get('/api/audio/command/stats')
async def get_command_processing_stats():
    try:
        if audio_command_processor is None:
            raise HTTPException(status_code=503, detail="Audio command processor is not available")
            
        stats = await audio_command_processor.get_processing_stats()
        return JSONResponse(content={
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
@app.get('/api/system/status')
async def get_system_status():
    """Get system status information"""
    try:
        import psutil
        import os
        
        # Get system info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check if services are running
        backend_status = "running"  # If we're responding, backend is running
        
        # Get recent logs (last 50 lines)
        logs = []
        log_file = "logs/backend.log"
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    logs = [line.strip() for line in lines[-50:] if line.strip()]
            except Exception:
                logs = ["Could not read log file"]
        
        return JSONResponse(content={
            "success": True,
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2)
            },
            "services": {
                "backend": backend_status,
                "frontend": "unknown"  # Frontend status would need to be checked separately
            },
            "logs": logs
        })
        
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "error": f"Failed to get system status: {str(e)}"
        })

@app.post('/api/system/logs')
async def get_system_logs(request: Request):
    """Get system logs with filtering options"""
    try:
        data = await request.json()
        log_type = data.get('type', 'backend')  # backend, frontend, system
        lines = data.get('lines', 100)
        
        logs = []
        log_files = {
            'backend': 'logs/backend.log',
            'frontend': 'logs/frontend.log',
            'system': 'logs/system.log'
        }
        
        log_file = log_files.get(log_type, 'logs/backend.log')
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    file_lines = f.readlines()
                    logs = [line.strip() for line in file_lines[-lines:] if line.strip()]
            except Exception as e:
                logs = [f"Error reading log file: {str(e)}"]
        else:
            logs = [f"Log file {log_file} not found"]
        
        return JSONResponse(content={
            "success": True,
            "logs": logs,
            "type": log_type,
            "count": len(logs)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")
