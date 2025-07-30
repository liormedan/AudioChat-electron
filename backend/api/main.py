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
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
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
codex/remove-lines-155163-for-clean-assignments
session_service = services['session_service']
chat_history_service = services['chat_history_service']
chat_service = services['chat_service']


# --- FastAPI App Initialization ---
app = create_app()

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
async def send_chat_message(request: SendMessageRequest):
    """Send a chat message and return the response"""
    if chat_service is None:
        raise HTTPException(status_code=503, detail="Chat service is not available")
    try:
        result = chat_service.send_message(request.session_id, request.message, request.user_id)
        return JSONResponse(content=result.to_dict())
    except SessionNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ModelNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/api/chat/stream')
async def stream_chat_message(request: SendMessageRequest):
    """Stream chat response using Server-Sent Events"""
    if chat_service is None:
        raise HTTPException(status_code=503, detail="Chat service is not available")

    async def event_generator():
        try:
            async for chunk in chat_service.stream_message(request.session_id, request.message, request.user_id):
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
