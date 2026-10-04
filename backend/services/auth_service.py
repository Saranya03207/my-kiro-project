"""
Authentication service for Smart Canteen Manager.
Handles session creation, validation, and management.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from sqlalchemy.orm import Session as DBSession
from backend.models.session import Session
from backend.schemas.auth import LoginRequest, SessionResponse


class AuthService:
    """
    Service class for authentication and session management.
    
    Responsibilities:
    - Generate unique session tokens
    - Create and store user sessions
    - Validate session tokens
    - Check session expiration
    - Invalidate sessions (logout)
    """
    
    @staticmethod
    def generate_session_token() -> str:
        """
        Generate a unique session token using UUID v4.
        
        Returns:
            Unique session token as string
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def create_session(
        db: DBSession,
        login_request: LoginRequest,
        expiry_hours: int = 24
    ) -> SessionResponse:
        """
        Create a new user session.
        
        Args:
            db: Database session
            login_request: Login credentials (user_id and role)
            expiry_hours: Session expiration time in hours (default 24)
            
        Returns:
            SessionResponse with token and session details
        """
        # Generate unique token
        token = AuthService.generate_session_token()
        
        # Calculate expiration timestamp
        expires_at = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
        
        # Create session record
        session = Session(
            user_id=login_request.user_id,
            role=login_request.role,
            token=token,
            expires_at=expires_at
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # SQLite returns timezone-naive datetimes, so we need to add UTC timezone info
        # to make it comparable with other timezone-aware datetimes
        expires_at_utc = session.expires_at.replace(tzinfo=timezone.utc)
        
        # Return response
        return SessionResponse(
            token=session.token,
            user_id=session.user_id,
            role=session.role,
            expires_at=expires_at_utc
        )
    
    @staticmethod
    def validate_session(db: DBSession, token: str) -> Optional[Session]:
        """
        Validate a session token and check expiration.
        
        Args:
            db: Database session
            token: Session token to validate
            
        Returns:
            Session object if valid and not expired, None otherwise
        """
        # Find session by token
        session = db.query(Session).filter(Session.token == token).first()
        
        if not session:
            return None
        
        # SQLite returns timezone-naive datetimes, add UTC timezone for comparison
        expires_at_utc = session.expires_at.replace(tzinfo=timezone.utc)
        
        # Check if session has expired
        if expires_at_utc < datetime.now(timezone.utc):
            # Delete expired session
            db.delete(session)
            db.commit()
            return None
        
        return session
    
    @staticmethod
    def invalidate_session(db: DBSession, token: str) -> bool:
        """
        Invalidate (delete) a session (logout).
        
        Args:
            db: Database session
            token: Session token to invalidate
            
        Returns:
            True if session was deleted, False if not found
        """
        session = db.query(Session).filter(Session.token == token).first()
        
        if session:
            db.delete(session)
            db.commit()
            return True
        
        return False
    
    @staticmethod
    def get_session_by_user_id(db: DBSession, user_id: str) -> Optional[Session]:
        """
        Get active session for a user.
        
        Args:
            db: Database session
            user_id: User identifier
            
        Returns:
            Active session if exists and not expired, None otherwise
        """
        session = db.query(Session).filter(
            Session.user_id == user_id,
            Session.expires_at > datetime.now(timezone.utc)
        ).first()
        
        return session
