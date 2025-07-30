from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import json


@dataclass
class ChatSession:
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


@dataclass
class Message:
    id: str
    session_id: str
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime
    model_id: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role,
            "content": self.content,
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


@dataclass
class ChatResponse:
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


class ChatError(Exception):
    """Base exception for chat-related errors."""


class SessionNotFoundError(ChatError):
    """Raised when a session cannot be found."""


class ModelNotAvailableError(ChatError):
    """Raised when no model is available for chat generation."""
