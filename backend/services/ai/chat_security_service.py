from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
# We will need access to the SessionService, so let's prepare for the import
# from backend.services.ai.session_service import SessionService 

class ChatSecurityService:
    """
    Provides security features for the chat API, including rate limiting,
    input sanitization, and session access validation.
    """

    def __init__(self):
        self.limiter = Limiter(key_func=get_remote_address, default_limits=["100 per minute"])
        # Add a placeholder for the session service
        self.session_service = None

    def set_session_service(self, session_service):
        """Allows setting the session service after initialization."""
        self.session_service = session_service

    def sanitize_input(self, text: str) -> str:
        # ... (this method remains the same)
        if text is None:
            return ""
        import re
        text = re.sub(r'<[^>]*>', '', text)
        return text.strip()

    def validate_session_access(self, session_id: str, user_id: str) -> bool:
        """
        Validates if a user has permission to access a specific chat session.
        """
        if not self.session_service:
            # If the service isn't set, we can't validate.
            # Depending on security policy, you might want to deny access by default.
            print("Warning: Session service not available for security validation.")
            return True # Fails open for now, but could be False

        session = self.session_service.get_session(session_id)

        # 1. Check if the session exists
        if not session:
            return False # Session not found, so access is denied

        # 2. Check if the session is associated with the user
        # (Assuming the Session object has a 'user_id' attribute)
        if session.user_id != user_id:
            return False # User does not own this session

        # 3. If all checks pass, grant access
        return True

    def check_rate_limit(self, request: Request):
        """
        Applies rate limiting to the incoming request.
        """
        try:
            self.limiter.check(request)
        except HTTPException as e:
            # Re-raise the HTTPException from slowapi
            raise e
        except Exception as e:
            # Handle other potential errors during rate limit check
            print(f"Error during rate limit check: {e}")
            raise HTTPException(status_code=500, detail="Error processing request")

# You can create a single instance to be used across the application
security_service = ChatSecurityService()