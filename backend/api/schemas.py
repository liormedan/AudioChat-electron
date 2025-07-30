from typing import Optional, Dict, Any
from pydantic import BaseModel


class SendMessageRequest(BaseModel):
    session_id: str
    message: str
    user_id: Optional[str] = None


class SessionCreateRequest(BaseModel):
    title: Optional[str] = None
    model_id: Optional[str] = None
    user_id: Optional[str] = None


class SessionUpdateRequest(BaseModel):
    title: Optional[str] = None
    model_id: Optional[str] = None
    is_archived: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
