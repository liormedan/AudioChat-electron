# Services package

# Core services that should always be available
try:
    from .utils.chat_service import ChatService, ChatMessage, ChatSession
except ImportError:
    ChatService = None
    ChatMessage = None
    ChatSession = None
try:
    from .llm_service import LLMService
except ImportError:
    LLMService = None

try:
    from .audio_editing_service import AudioEditingService
except ImportError:
    AudioEditingService = None

try:
    from .advanced_audio_editing_service import AdvancedAudioEditingService
except ImportError:
    AdvancedAudioEditingService = None

try:
    from .file_upload_service import FileUploadService
except ImportError:
    FileUploadService = None

try:
    from .audio_metadata_service import AudioMetadataService
except ImportError:
    AudioMetadataService = None

try:
    from .audio_command_interpreter import AudioCommandInterpreter
except ImportError:
    AudioCommandInterpreter = None

try:
    from .audio_command_processor import AudioCommandProcessor
except ImportError:
    AudioCommandProcessor = None

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
    from .cloud_storage_service import CloudStorageService
except ImportError:
    CloudStorageService = None

try:
    from .export_service import ExportService
except ImportError:
    ExportService = None

try:
    from .file_service import FileService
except ImportError:
    FileService = None

try:
    from .file_stats_data_manager import FileStatsDataManager
except ImportError:
    FileStatsDataManager = None

__all__ = [
    'ChatService',
    'ChatMessage', 
    'ChatSession',
    'LLMService',
    'SettingsService',
    'UsageService',
    'ProfileService'
]

# Add to __all__ only if imported successfully
if AudioEditingService:
    __all__.append('AudioEditingService')
if AudioStorageService:
    __all__.append('AudioStorageService')
if CloudStorageService:
    __all__.append('CloudStorageService')
if ExportService:
    __all__.append('ExportService')
if FileService:
    __all__.append('FileService')
if FileStatsDataManager:
    __all__.append('FileStatsDataManager')

