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
# from models.llm_models import LLMProvider # Import the model for type hinting and serialization

# --- Initialize Services ---
# Create an instance of the service that the server will use
llm_service = LLMService()

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
