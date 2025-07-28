import os
import uuid
import librosa
import soundfile as sf
from typing import Dict, Any, Optional, List
from werkzeug.utils import secure_filename
from mutagen import File as MutagenFile
import tempfile
import shutil
import mimetypes

# Try to import python-magic, fallback to mimetypes if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    print("Warning: python-magic not available, using mimetypes for file type detection")

class FileUploadService:
    """Service for handling audio file uploads with validation and metadata extraction."""
    
    # Supported audio formats
    ALLOWED_EXTENSIONS = {
        'wav', 'mp3', 'flac', 'ogg', 'aac', 'm4a', 'wma', 'aiff', 'au'
    }
    
    # MIME types for audio files
    ALLOWED_MIME_TYPES = {
        'audio/wav', 'audio/wave', 'audio/x-wav',
        'audio/mpeg', 'audio/mp3',
        'audio/flac',
        'audio/ogg', 'audio/vorbis',
        'audio/aac', 'audio/x-aac',
        'audio/mp4', 'audio/x-m4a',
        'audio/x-ms-wma',
        'audio/aiff', 'audio/x-aiff',
        'audio/basic'
    }
    
    # Maximum file size (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    def __init__(self, upload_directory: str = None):
        """
        Initialize the file upload service.
        
        Args:
            upload_directory: Directory to store uploaded files. If None, uses temp directory.
        """
        if upload_directory is None:
            self.upload_directory = os.path.join(tempfile.gettempdir(), 'audio_chat_uploads')
        else:
            self.upload_directory = upload_directory
            
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_directory, exist_ok=True)
    
    def validate_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Validate uploaded audio file.
        
        Args:
            file_data: Raw file data
            filename: Original filename
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Check file size
            if len(file_data) > self.MAX_FILE_SIZE:
                return {
                    "valid": False,
                    "error": f"File size ({len(file_data)} bytes) exceeds maximum allowed size ({self.MAX_FILE_SIZE} bytes)"
                }
            
            # Check file extension
            file_extension = self._get_file_extension(filename)
            if file_extension not in self.ALLOWED_EXTENSIONS:
                return {
                    "valid": False,
                    "error": f"File extension '{file_extension}' is not supported. Allowed: {', '.join(self.ALLOWED_EXTENSIONS)}"
                }
            
            # Check MIME type
            mime_type = None
            if MAGIC_AVAILABLE:
                try:
                    mime_type = magic.from_buffer(file_data, mime=True)
                    if mime_type not in self.ALLOWED_MIME_TYPES:
                        return {
                            "valid": False,
                            "error": f"File type '{mime_type}' is not supported. This doesn't appear to be a valid audio file."
                        }
                except Exception as e:
                    print(f"Warning: Could not determine MIME type with magic: {e}")
                    mime_type = None
            
            # Fallback to mimetypes if magic is not available or failed
            if mime_type is None:
                mime_type, _ = mimetypes.guess_type(filename)
                if mime_type and not mime_type.startswith('audio/'):
                    return {
                        "valid": False,
                        "error": f"File type '{mime_type}' is not supported. This doesn't appear to be a valid audio file."
                    }
            
            # Try to validate as audio file by attempting to load it
            temp_file = None
            try:
                # Create temporary file for validation
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}')
                temp_file.write(file_data)
                temp_file.close()
                
                # Try to load with librosa to validate it's a proper audio file
                y, sr = librosa.load(temp_file.name, sr=None, duration=1.0)  # Load only first second for validation
                
                if len(y) == 0:
                    return {
                        "valid": False,
                        "error": "File appears to be empty or corrupted"
                    }
                
            except Exception as e:
                return {
                    "valid": False,
                    "error": f"File is not a valid audio file: {str(e)}"
                }
            finally:
                # Clean up temporary file
                if temp_file and os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
            
            return {
                "valid": True,
                "file_size": len(file_data),
                "file_extension": file_extension,
                "mime_type": mime_type if 'mime_type' in locals() else f"audio/{file_extension}"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    def save_uploaded_file(self, file_data: bytes, original_filename: str) -> Dict[str, Any]:
        """
        Save uploaded file to disk with a unique filename.
        
        Args:
            file_data: Raw file data
            original_filename: Original filename from upload
            
        Returns:
            Dictionary with file information
        """
        try:
            # Generate unique filename
            file_extension = self._get_file_extension(original_filename)
            unique_id = str(uuid.uuid4())
            secure_name = secure_filename(original_filename)
            base_name = os.path.splitext(secure_name)[0]
            
            # Create unique filename: originalname_uuid.ext
            unique_filename = f"{base_name}_{unique_id}.{file_extension}"
            file_path = os.path.join(self.upload_directory, unique_filename)
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            return {
                "success": True,
                "file_id": unique_id,
                "original_filename": original_filename,
                "stored_filename": unique_filename,
                "file_path": file_path,
                "file_size": len(file_data)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save file: {str(e)}"
            }
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary with metadata information
        """
        try:
            metadata = {}
            
            # Extract audio properties using librosa
            try:
                y, sr = librosa.load(file_path, sr=None)
                duration = librosa.get_duration(y=y, sr=sr)
                
                metadata.update({
                    "duration": duration,
                    "sample_rate": sr,
                    "channels": 1 if len(y.shape) == 1 else y.shape[0],
                    "samples": len(y),
                    "format_info": {
                        "librosa_loaded": True,
                        "shape": y.shape
                    }
                })
            except Exception as e:
                print(f"Warning: Could not extract audio properties with librosa: {e}")
            
            # Extract metadata using mutagen
            try:
                audio_file = MutagenFile(file_path)
                if audio_file is not None:
                    # Get basic info
                    if hasattr(audio_file, 'info'):
                        info = audio_file.info
                        metadata.update({
                            "bitrate": getattr(info, 'bitrate', None),
                            "length": getattr(info, 'length', None),
                            "channels": getattr(info, 'channels', None),
                            "sample_rate": getattr(info, 'sample_rate', None)
                        })
                    
                    # Get tags
                    tags = {}
                    if audio_file.tags:
                        for key, value in audio_file.tags.items():
                            if isinstance(value, list) and len(value) == 1:
                                tags[key] = value[0]
                            else:
                                tags[key] = value
                    
                    metadata["tags"] = tags
                    
            except Exception as e:
                print(f"Warning: Could not extract metadata with mutagen: {e}")
            
            # Get file system info
            stat = os.stat(file_path)
            metadata.update({
                "file_size": stat.st_size,
                "created_time": stat.st_ctime,
                "modified_time": stat.st_mtime,
                "file_extension": self._get_file_extension(file_path)
            })
            
            return {
                "success": True,
                "metadata": metadata
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to extract metadata: {str(e)}"
            }
    
    def upload_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Complete file upload process: validate, save, and extract metadata.
        
        Args:
            file_data: Raw file data
            filename: Original filename
            
        Returns:
            Dictionary with complete upload results
        """
        try:
            # Step 1: Validate file
            validation_result = self.validate_file(file_data, filename)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"],
                    "stage": "validation"
                }
            
            # Step 2: Save file
            save_result = self.save_uploaded_file(file_data, filename)
            if not save_result["success"]:
                return {
                    "success": False,
                    "error": save_result["error"],
                    "stage": "saving"
                }
            
            # Step 3: Extract metadata
            metadata_result = self.extract_metadata(save_result["file_path"])
            
            # Combine results
            result = {
                "success": True,
                "file_id": save_result["file_id"],
                "original_filename": save_result["original_filename"],
                "stored_filename": save_result["stored_filename"],
                "file_path": save_result["file_path"],
                "file_size": save_result["file_size"],
                "validation": validation_result,
                "metadata": metadata_result.get("metadata", {}) if metadata_result["success"] else {}
            }
            
            if not metadata_result["success"]:
                result["metadata_warning"] = metadata_result["error"]
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Upload process failed: {str(e)}",
                "stage": "general"
            }
    
    def get_uploaded_files(self) -> List[Dict[str, Any]]:
        """
        Get list of all uploaded files.
        
        Returns:
            List of file information dictionaries
        """
        try:
            files = []
            for filename in os.listdir(self.upload_directory):
                file_path = os.path.join(self.upload_directory, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    files.append({
                        "filename": filename,
                        "file_path": file_path,
                        "file_size": stat.st_size,
                        "created_time": stat.st_ctime,
                        "modified_time": stat.st_mtime
                    })
            
            return files
            
        except Exception as e:
            print(f"Error listing uploaded files: {e}")
            return []
    
    def delete_uploaded_file(self, file_id: str) -> Dict[str, Any]:
        """
        Delete an uploaded file by its ID.
        
        Args:
            file_id: Unique file identifier
            
        Returns:
            Dictionary with deletion results
        """
        try:
            # Find file with matching ID
            for filename in os.listdir(self.upload_directory):
                if file_id in filename:
                    file_path = os.path.join(self.upload_directory, filename)
                    os.remove(file_path)
                    return {
                        "success": True,
                        "message": f"File {filename} deleted successfully"
                    }
            
            return {
                "success": False,
                "error": f"File with ID {file_id} not found"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete file: {str(e)}"
            }
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase."""
        return os.path.splitext(filename)[1][1:].lower()