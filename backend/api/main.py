import sys
import os

# Add the parent directory (backend) to sys.path for module discovery
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from typing import Optional, List, Dict
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# --- Import Services ---
from backend.services.ai.llm_service import LLMService
from backend.services.audio.editing import AudioEditingService
from backend.services.storage.file_upload import FileUploadService
from backend.services.audio.metadata import AudioMetadataService
from backend.services.ai.command_processor import AudioCommandProcessor

def initialize_services():
    """
    Initialize all backend services
    אתחול כל שירותי הבקאנד
    """
    # Create an instance of the service that the server will use
    llm_service = LLMService()
    audio_editing_service = AudioEditingService()
    file_upload_service = FileUploadService()
    audio_metadata_service = AudioMetadataService()

    # Initialize the command processor with all required services
    audio_command_processor = AudioCommandProcessor(
        llm_service=llm_service,
        audio_editing_service=audio_editing_service,
        audio_metadata_service=audio_metadata_service
    )
    
    return {
        'llm_service': llm_service,
        'audio_editing_service': audio_editing_service,
        'file_upload_service': file_upload_service,
        'audio_metadata_service': audio_metadata_service,
        'audio_command_processor': audio_command_processor
    }

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

# --- FastAPI App Initialization ---
app = create_app()

# --- API Endpoints ---

@app.get('/')
async def read_root():
    return {"status": "ok", "message": "Audio Chat Python Backend is running!"}

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
        providers = llm_service.get_all_providers()
        provider_list = [p.to_dict() for p in providers]
        return JSONResponse(content=provider_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve providers: {e}")

@app.get('/api/llm/models')
async def get_all_models(provider: Optional[str] = None):
    try:
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
        success = llm_service.set_active_model(model_id)
        return JSONResponse(content={"success": success})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set active model: {e}")

@app.post('/api/llm/chat/completion')
async def chat_completion_endpoint(messages: List[Dict[str, str]]):
    try:
        response = llm_service.generate_chat_response(messages)
        if response:
            return JSONResponse(content=response.to_dict())
        else:
            raise HTTPException(status_code=500, detail="Failed to get response from LLM")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/audio/command/interpret')
async def interpret_audio_command(request: Request):
    try:
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
        stats = await audio_command_processor.get_processing_stats()
        return JSONResponse(content={
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
