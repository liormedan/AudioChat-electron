from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserProfile:
    """Simple user profile model."""

    id: str
    display_name: str
    email: str
    avatar_path: Optional[str]
    created_at: datetime
    updated_at: datetime
