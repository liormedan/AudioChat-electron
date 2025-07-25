# Services package

from .chat_service import ChatService, ChatMessage, ChatSession
from .llm_service import LLMService
from .settings_service import SettingsService
from .usage_service import UsageService

# Import other services if they exist
try:
    from .audio_editing_service import AudioEditingService
except ImportError:
    AudioEditingService = None

try:
    from .audio_storage_service import AudioStorageService
except ImportError:
    AudioStorageService = None

try:
    from .export_service import ExportService
except ImportError:
    ExportService = None

try:
    from .file_service import FileService
except ImportError:
    FileService = None

__all__ = [
    'ChatService',
    'ChatMessage', 
    'ChatSession',
    'LLMService',
    'SettingsService',
    'UsageService'
]

# Add to __all__ only if imported successfully
if AudioEditingService:
    __all__.append('AudioEditingService')
if AudioStorageService:
    __all__.append('AudioStorageService')
if ExportService:
    __all__.append('ExportService')
if FileService:
    __all__.append('FileService')
