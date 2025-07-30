from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import json
from enum import Enum


class MessageRole(Enum):
    """Possible roles for a chat message."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(Enum):
    """Supported message types."""

    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    FILE = "file"


class MessageRole(Enum):
    """Message role types"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class SessionStatus(Enum):
    """Session status types"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


@dataclass
class ChatSession:
    """Chat session metadata."""
    id: str
    title: str
    model_id: str
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int
    is_archived: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "model_id": self.model_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "message_count": self.message_count,
            "is_archived": self.is_archived,
            "metadata": self.metadata,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "ChatSession":
        return cls(
            id=row[0],
            title=row[1],
            model_id=row[2],
            user_id=row[3],
            created_at=datetime.fromisoformat(row[4]),
            updated_at=datetime.fromisoformat(row[5]),
            message_count=row[6],
            is_archived=bool(row[7]),
            metadata=json.loads(row[8]) if row[8] else {},
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSession":
        return cls(
            id=data["id"],
            title=data["title"],
            model_id=data["model_id"],
            user_id=data.get("user_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            message_count=data["message_count"],
            is_archived=data.get("is_archived", False),
            metadata=data.get("metadata", {}),
        )

@dataclass
class Message:
    """Single chat message."""
    id: str
    session_id: str
    content: str
    timestamp: datetime
    role: MessageRole = MessageRole.USER
    type: MessageType = MessageType.TEXT
    model_id: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.role, str):
            self.role = MessageRole(self.role)
        if isinstance(self.type, str):
            self.type = MessageType(self.type)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role.value,
            "content": self.content,
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "model_id": self.model_id,
            "tokens_used": self.tokens_used,
            "response_time": self.response_time,
            "metadata": self.metadata,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "Message":
        return cls(
            id=row[0],
            session_id=row[1],
            role=row[2],
            content=row[3],
            timestamp=datetime.fromisoformat(row[4]),
            model_id=row[5],
            tokens_used=row[6],
            response_time=row[7],
            metadata=json.loads(row[8]) if row[8] else {},
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            id=data["id"],
            session_id=data["session_id"],
            role=data.get("role", MessageRole.USER.value),
            content=data["content"],
            type=data.get("type", MessageType.TEXT.value),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            model_id=data.get("model_id"),
            tokens_used=data.get("tokens_used"),
            response_time=data.get("response_time"),
            metadata=data.get("metadata", {}),
        )

@dataclass
class ChatResponse:
    """Response from the model for a chat message."""
    content: str
    model_id: str
    tokens_used: int
    response_time: float
    success: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model_id": self.model_id,
            "tokens_used": self.tokens_used,
            "response_time": self.response_time,
            "success": self.success,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatResponse":
        return cls(
            content=data["content"],
            model_id=data["model_id"],
            tokens_used=data["tokens_used"],
            response_time=data["response_time"],
            success=data["success"],
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {}),
        )

# Exceptions
class ChatError(Exception):
    """Base exception for chat-related errors."""

class SessionNotFoundError(ChatError):
    """Raised when a session cannot be found."""

class ModelNotAvailableError(ChatError):
    """Raised when no model is available for chat generation."""

