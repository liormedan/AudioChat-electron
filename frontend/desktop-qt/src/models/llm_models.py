from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
import json
from enum import Enum


class ProviderStatus(Enum):
    """סטטוס ספק LLM"""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    TESTING = "testing"
    ERROR = "error"


class ModelCapability(Enum):
    """יכולות מודל LLM"""
    TEXT_GENERATION = "text_generation"
    CHAT = "chat"
    CODE_GENERATION = "code_generation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    AUDIO_TRANSCRIPTION = "audio_transcription"
    AUDIO_ANALYSIS = "audio_analysis"


@dataclass
class LLMProvider:
    """מודל ספק LLM"""
    name: str
    api_base_url: str
    supported_models: List[str]
    api_key: Optional[str] = None
    is_connected: bool = False
    connection_status: ProviderStatus = ProviderStatus.DISCONNECTED
    last_test_date: Optional[datetime] = None
    error_message: Optional[str] = None
    rate_limit: Optional[int] = None  # בקשות לדקה
    cost_per_1k_tokens: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def test_connection(self) -> bool:
        """בדיקת חיבור לספק"""
        if not self.api_key:
            self.connection_status = ProviderStatus.ERROR
            self.error_message = "API key is required"
            return False
        
        # כאן תהיה לוגיקת בדיקת חיבור אמיתית
        # לעת עתה נחזיר True אם יש API key
        self.connection_status = ProviderStatus.CONNECTED
        self.is_connected = True
        self.last_test_date = datetime.now()
        self.error_message = None
        return True
    
    def disconnect(self) -> None:
        """ניתוק מהספק"""
        self.is_connected = False
        self.connection_status = ProviderStatus.DISCONNECTED
        self.error_message = None
    
    def set_error(self, error_message: str) -> None:
        """הגדרת שגיאה"""
        self.connection_status = ProviderStatus.ERROR
        self.is_connected = False
        self.error_message = error_message
    
    @property
    def status_display(self) -> str:
        """תצוגת סטטוס לממשק המשתמש"""
        status_map = {
            ProviderStatus.CONNECTED: "🟢 מחובר",
            ProviderStatus.DISCONNECTED: "🔴 מנותק",
            ProviderStatus.TESTING: "🟡 בודק חיבור",
            ProviderStatus.ERROR: "❌ שגיאה"
        }
        return status_map.get(self.connection_status, "❓ לא ידוע")
    
    def to_dict(self) -> Dict[str, Any]:
        """המרת האובייקט למילון"""
        return {
            "name": self.name,
            "api_base_url": self.api_base_url,
            "supported_models": self.supported_models,
            "api_key": self.api_key,  # יוצפן בשירות
            "is_connected": self.is_connected,
            "connection_status": self.connection_status.value,
            "last_test_date": self.last_test_date.isoformat() if self.last_test_date else None,
            "error_message": self.error_message,
            "rate_limit": self.rate_limit,
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMProvider':
        """יצירת אובייקט מתוך מילון"""
        # המרת תאריך מ-ISO לאובייקט datetime
        last_test_date = None
        if data.get("last_test_date"):
            last_test_date = datetime.fromisoformat(data["last_test_date"])
        
        return cls(
            name=data["name"],
            api_base_url=data["api_base_url"],
            supported_models=data["supported_models"],
            api_key=data.get("api_key"),
            is_connected=data.get("is_connected", False),
            connection_status=ProviderStatus(data.get("connection_status", "disconnected")),
            last_test_date=last_test_date,
            error_message=data.get("error_message"),
            rate_limit=data.get("rate_limit"),
            cost_per_1k_tokens=data.get("cost_per_1k_tokens"),
            metadata=data.get("metadata", {})
        )


@dataclass
class LLMModel:
    """מודל LLM"""
    id: str
    name: str
    provider: str
    description: str
    max_tokens: int
    cost_per_token: float
    capabilities: List[ModelCapability]
    is_active: bool = False
    is_available: bool = True
    context_window: int = 4096
    training_data_cutoff: Optional[str] = None
    version: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def display_name(self) -> str:
        """שם תצוגה"""
        return f"{self.provider} - {self.name}"
    
    @property
    def capabilities_display(self) -> str:
        """תצוגת יכולות"""
        capability_map = {
            ModelCapability.TEXT_GENERATION: "יצירת טקסט",
            ModelCapability.CHAT: "שיחה",
            ModelCapability.CODE_GENERATION: "יצירת קוד",
            ModelCapability.TRANSLATION: "תרגום",
            ModelCapability.SUMMARIZATION: "סיכום",
            ModelCapability.AUDIO_TRANSCRIPTION: "תמלול אודיו",
            ModelCapability.AUDIO_ANALYSIS: "ניתוח אודיו"
        }
        return ", ".join([capability_map.get(cap, cap.value) for cap in self.capabilities])
    
    @property
    def cost_per_1k_tokens(self) -> float:
        """עלות לאלף טוקנים"""
        return self.cost_per_token * 1000
    
    def has_capability(self, capability: ModelCapability) -> bool:
        """בדיקה האם למודל יש יכולת מסוימת"""
        return capability in self.capabilities
    
    def estimate_cost(self, token_count: int) -> float:
        """הערכת עלות לפי מספר טוקנים"""
        return token_count * self.cost_per_token
    
    def to_dict(self) -> Dict[str, Any]:
        """המרת האובייקט למילון"""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "description": self.description,
            "max_tokens": self.max_tokens,
            "cost_per_token": self.cost_per_token,
            "capabilities": [cap.value for cap in self.capabilities],
            "is_active": self.is_active,
            "is_available": self.is_available,
            "context_window": self.context_window,
            "training_data_cutoff": self.training_data_cutoff,
            "version": self.version,
            "parameters": self.parameters,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMModel':
        """יצירת אובייקט מתוך מילון"""
        capabilities = [ModelCapability(cap) for cap in data.get("capabilities", [])]
        
        return cls(
            id=data["id"],
            name=data["name"],
            provider=data["provider"],
            description=data["description"],
            max_tokens=data["max_tokens"],
            cost_per_token=data["cost_per_token"],
            capabilities=capabilities,
            is_active=data.get("is_active", False),
            is_available=data.get("is_available", True),
            context_window=data.get("context_window", 4096),
            training_data_cutoff=data.get("training_data_cutoff"),
            version=data.get("version"),
            parameters=data.get("parameters", {}),
            metadata=data.get("metadata", {})
        )


@dataclass
class UsageRecord:
    """רשומת שימוש ב-LLM"""
    id: str
    timestamp: datetime
    model_id: str
    provider: str
    tokens_used: int
    cost: float
    response_time: float  # בשניות
    success: bool
    error_message: Optional[str] = None
    request_type: str = "chat"  # chat, completion, transcription, etc.
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def cost_formatted(self) -> str:
        """עלות בפורמט קריא"""
        if self.cost < 0.01:
            return f"${self.cost:.4f}"
        elif self.cost < 1:
            return f"${self.cost:.3f}"
        else:
            return f"${self.cost:.2f}"
    
    @property
    def response_time_formatted(self) -> str:
        """זמן תגובה בפורמט קריא"""
        if self.response_time < 1:
            return f"{self.response_time * 1000:.0f}ms"
        else:
            return f"{self.response_time:.1f}s"
    
    @property
    def timestamp_formatted(self) -> str:
        """זמן בפורמט קריא"""
        now = datetime.now()
        
        # אם התאריך הוא היום
        if self.timestamp.date() == now.date():
            return f"היום, {self.timestamp.strftime('%H:%M')}"
        
        # אם התאריך הוא אתמול
        yesterday = now.date().replace(day=now.day-1)
        if self.timestamp.date() == yesterday:
            return f"אתמול, {self.timestamp.strftime('%H:%M')}"
        
        # אחרת, החזר תאריך מלא
        return self.timestamp.strftime("%d/%m/%Y, %H:%M")
    
    @property
    def status_display(self) -> str:
        """תצוגת סטטוס"""
        if self.success:
            return "✅ הצליח"
        else:
            return "❌ נכשל"
    
    def to_dict(self) -> Dict[str, Any]:
        """המרת האובייקט למילון"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "model_id": self.model_id,
            "provider": self.provider,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "response_time": self.response_time,
            "success": self.success,
            "error_message": self.error_message,
            "request_type": self.request_type,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageRecord':
        """יצירת אובייקט מתוך מילון"""
        return cls(
            id=data["id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            model_id=data["model_id"],
            provider=data["provider"],
            tokens_used=data["tokens_used"],
            cost=data["cost"],
            response_time=data["response_time"],
            success=data["success"],
            error_message=data.get("error_message"),
            request_type=data.get("request_type", "chat"),
            user_id=data.get("user_id"),
            session_id=data.get("session_id"),
            metadata=data.get("metadata", {})
        )


@dataclass
class LLMParameters:
    """פרמטרי מודל LLM"""
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    
    def validate(self) -> bool:
        """בדיקת תקינות הפרמטרים"""
        if not (0.0 <= self.temperature <= 2.0):
            return False
        if not (0.0 <= self.top_p <= 1.0):
            return False
        if not (-2.0 <= self.frequency_penalty <= 2.0):
            return False
        if not (-2.0 <= self.presence_penalty <= 2.0):
            return False
        if self.max_tokens <= 0:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """המרת הפרמטרים למילון"""
        return {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stop_sequences": self.stop_sequences
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMParameters':
        """יצירת פרמטרים מתוך מילון"""
        return cls(
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 1000),
            top_p=data.get("top_p", 0.9),
            frequency_penalty=data.get("frequency_penalty", 0.0),
            presence_penalty=data.get("presence_penalty", 0.0),
            stop_sequences=data.get("stop_sequences", [])
        )
    
    @classmethod
    def get_preset(cls, preset_name: str) -> 'LLMParameters':
        """קבלת פרסט פרמטרים"""
        presets = {
            "creative": cls(temperature=0.9, max_tokens=1500, top_p=0.95, frequency_penalty=0.3),
            "balanced": cls(temperature=0.7, max_tokens=1000, top_p=0.9, frequency_penalty=0.0),
            "precise": cls(temperature=0.3, max_tokens=800, top_p=0.8, frequency_penalty=0.0),
            "code": cls(temperature=0.1, max_tokens=2000, top_p=0.95, frequency_penalty=0.0),
            "chat": cls(temperature=0.8, max_tokens=1200, top_p=0.9, frequency_penalty=0.1)
        }
        return presets.get(preset_name, cls())
