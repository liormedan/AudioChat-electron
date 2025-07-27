import sys
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# --- Setup Python Path ---
# This ensures that we can import modules from the 'src' directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(CURRENT_DIR, 'my_audio_app', 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# --- Import Services ---
# Now we can safely import our services
from services.llm_service import LLMService
from services.audio_editing_service import AudioEditingService
from services.file_upload_service import FileUploadService
# from models.llm_models import LLMProvider # Import the model for type hinting and serialization

# --- Initialize Services ---
# Create an instance of the service that the server will use
llm_service = LLMService()
audio_editing_service = AudioEditingService()
file_upload_service = FileUploadService()

# --- Flask App Initialization ---
app = Flask(__name__)
# Enable CORS to allow requests from the Electron frontend (which runs on a different origin)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- API Endpoints ---

@app.route('/')
def index():
    """A simple health check endpoint to confirm the server is running."""
    return jsonify({"status": "ok", "message": "Audio Chat Python Backend is running!"})

@app.route('/api/files/list', methods=['POST'])
def list_files_endpoint():
    """
    Endpoint to list files in a directory based on a glob pattern.
    """
    data = request.get_json()
    path = data.get('path', '.')
    pattern = data.get('pattern', '**/*')
    recursive = data.get('recursive', True)

    try:
        # Assuming you have a FileService or similar to handle file listing
        # For now, a simple glob implementation
        import glob
        files = [os.path.abspath(f) for f in glob.glob(os.path.join(path, pattern), recursive=recursive)]
        return jsonify(files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/audio/upload', methods=['POST'])
def upload_audio_file():
    """
    Endpoint to upload audio files with validation and metadata extraction.
    Expects multipart/form-data with 'file' field.
    """
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Check if file was actually selected
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Read file data
        file_data = file.read()
        original_filename = file.filename
        
        # Process upload using file upload service
        result = file_upload_service.upload_file(file_data, original_filename)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": "File uploaded successfully",
                "file_id": result["file_id"],
                "original_filename": result["original_filename"],
                "stored_filename": result["stored_filename"],
                "file_size": result["file_size"],
                "metadata": result["metadata"],
                "validation": result["validation"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result["error"],
                "stage": result.get("stage", "unknown")
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Upload failed: {str(e)}",
            "stage": "server_error"
        }), 500

@app.route('/api/audio/files', methods=['GET'])
def list_uploaded_files():
    """
    Endpoint to list all uploaded audio files.
    """
    try:
        files = file_upload_service.get_uploaded_files()
        return jsonify({
            "success": True,
            "files": files,
            "count": len(files)
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to list files: {str(e)}"
        }), 500

@app.route('/api/audio/files/<file_id>', methods=['DELETE'])
def delete_uploaded_file(file_id):
    """
    Endpoint to delete an uploaded audio file by ID.
    """
    try:
        result = file_upload_service.delete_uploaded_file(file_id)
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": result["message"]
            })
        else:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to delete file: {str(e)}"
        }), 500

@app.route('/api/audio/metadata/<file_id>', methods=['GET'])
def get_file_metadata(file_id):
    """
    Endpoint to get metadata for a specific uploaded file.
    """
    try:
        # Find file by ID
        files = file_upload_service.get_uploaded_files()
        target_file = None
        
        for file_info in files:
            if file_id in file_info["filename"]:
                target_file = file_info
                break
        
        if not target_file:
            return jsonify({
                "success": False,
                "error": f"File with ID {file_id} not found"
            }), 404
        
        # Extract metadata
        metadata_result = file_upload_service.extract_metadata(target_file["file_path"])
        
        if metadata_result["success"]:
            return jsonify({
                "success": True,
                "file_info": target_file,
                "metadata": metadata_result["metadata"]
            })
        else:
            return jsonify({
                "success": False,
                "error": metadata_result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get metadata: {str(e)}"
        }), 500

@app.route('/api/audio/transcribe', methods=['POST'])
def transcribe_audio_endpoint():
    data = request.get_json()
    audio_base64 = data.get('audio_base64')
    if not audio_base64:
        return jsonify({"error": "audio_base64 is required"}), 400

    try:
        transcription = audio_editing_service.transcribe_audio(audio_base64)
        return jsonify({"transcription": transcription})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/audio/process-command', methods=['POST'])
def process_audio_command():
    """
    Endpoint to process natural language audio editing commands.
    """
    data = request.get_json()
    command = data.get('command')
    filename = data.get('filename')
    
    if not command:
        return jsonify({"error": "command is required"}), 400
    if not filename:
        return jsonify({"error": "filename is required"}), 400

    try:
        # Use LLM to interpret the command and execute audio editing
        response = audio_editing_service.process_natural_language_command(command, filename)
        return jsonify({
            "response": response.get("message", "Command processed successfully"),
            "status": response.get("status", "completed"),
            "processed_file": response.get("processed_file"),
            "details": response.get("details")
        })
    except Exception as e:
        return jsonify({"error": f"Failed to process command: {str(e)}"}), 500

# --- LLM Endpoints ---
@app.route('/api/llm/providers', methods=['GET'])
def get_all_providers():
    """Endpoint to retrieve all available LLM providers."""
    try:
        providers = llm_service.get_all_providers()
        # Convert each provider object to a dictionary for JSON serialization
        # Note: You will need to add a `to_dict()` method to your LLMProvider class.
        provider_list = [p.to_dict() for p in providers]
        return jsonify(provider_list)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve providers: {e}"}), 500

@app.route('/api/llm/models', methods=['GET'])
def get_all_models():
    """Endpoint to retrieve all available LLM models, optionally filtered by provider."""
    provider_name = request.args.get('provider')
    try:
        if provider_name:
            models = llm_service.get_models_by_provider(provider_name)
        else:
            models = llm_service.get_all_models()
        model_list = [m.to_dict() for m in models]
        return jsonify(model_list)
    except Exception as e:
        return jsonify({"error": f"Failed to retrieve models: {e}"}), 500

@app.route('/api/llm/active-model', methods=['GET', 'POST'])
def active_model_endpoint():
    """Endpoint to get or set the active LLM model."""
    if request.method == 'POST':
        data = request.get_json()
        model_id = data.get('model_id')
        if not model_id:
            return jsonify({"error": "model_id is required"}), 400
        try:
            success = llm_service.set_active_model(model_id)
            return jsonify({"success": success})
        except Exception as e:
            return jsonify({"error": f"Failed to set active model: {e}"}), 500
    else: # GET
        try:
            active_model = llm_service.get_active_model()
            if active_model:
                return jsonify(active_model.to_dict())
            else:
                return jsonify(None)
        except Exception as e:
            return jsonify({"error": f"Failed to retrieve active model: {e}"}), 500

@app.route('/api/llm/chat/completion', methods=['POST'])
def chat_completion_endpoint():
    """Endpoint for chat completion with the active LLM."""
    data = request.get_json()
    messages = data.get('messages')
    if not messages:
        return jsonify({"error": "messages are required"}), 400

    try:
        response = llm_service.generate_chat_response(messages)
        if response:
            return jsonify(response.to_dict())
        else:
            return jsonify({"error": "Failed to get response from LLM"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Main Execution Block ---
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
