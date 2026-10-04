"""
Unit tests for authentication service.
Tests session creation, validation, and management.
"""
import pytest
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models.session import Session
from backend.schemas.auth import LoginRequest
from backend.services.auth_service import AuthService


@pytest.fixture
def db_session():
    """Create in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


class TestGenerateSessionToken:
    """Test session token generation."""
    
    def test_generates_non_empty_token(self):
        """Token generation should return non-empty string."""
        token = AuthService.generate_session_token()
        assert token
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_generates_unique_tokens(self):
        """Multiple calls should generate different tokens."""
        token1 = AuthService.generate_session_token()
        token2 = AuthService.generate_session_token()
        token3 = AuthService.generate_session_token()
        
        assert token1 != token2
        assert token2 != token3
        assert token1 != token3
    
    def test_token_format_is_uuid(self):
        """Token should be a valid UUID format."""
        token = AuthService.generate_session_token()
        # UUID v4 format: 8-4-4-4-12 characters
        parts = token.split('-')
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12


class TestCreateSession:
    """Test session creation."""
    
    def test_creates_session_for_student(self, db_session):
        """Should create session for student user."""
        login_request = LoginRequest(user_id="S001", role="student")
        
        response = AuthService.create_session(db_session, login_request)
        
        assert response.token
        assert response.user_id == "S001"
        assert response.role == "student"
        assert response.expires_at > datetime.now(timezone.utc)
    
    def test_creates_session_for_admin(self, db_session):
        """Should create session for admin user."""
        login_request = LoginRequest(user_id="admin123", role="admin")
        
        response = AuthService.create_session(db_session, login_request)
        
        assert response.token
        assert response.user_id == "admin123"
        assert response.role == "admin"
        assert response.expires_at > datetime.now(timezone.utc)
    
    def test_session_stored_in_database(self, db_session):
        """Session should be persisted to database."""
        login_request = LoginRequest(user_id="S001", role="student")
        
        response = AuthService.create_session(db_session, login_request)
        
        # Query database to verify
        stored_session = db_session.query(Session).filter(
            Session.token == response.token
        ).first()
        
        assert stored_session is not None
        assert stored_session.user_id == "S001"
        assert stored_session.role == "student"
    
    def test_default_expiry_is_24_hours(self, db_session):
        """Default session expiry should be 24 hours."""
        login_request = LoginRequest(user_id="S001", role="student")
        
        before = datetime.now(timezone.utc) + timedelta(hours=24)
        response = AuthService.create_session(db_session, login_request)
        after = datetime.now(timezone.utc) + timedelta(hours=24)
        
        assert before <= response.expires_at <= after + timedelta(seconds=1)
    
    def test_custom_expiry_hours(self, db_session):
        """Should respect custom expiry hours."""
        login_request = LoginRequest(user_id="S001", role="student")
        
        response = AuthService.create_session(
            db_session,
            login_request,
            expiry_hours=1
        )
        
        expected_expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        # Allow 2 second tolerance
        assert abs((response.expires_at - expected_expiry).total_seconds()) < 2
    
    def test_token_is_unique(self, db_session):
        """Each session should have unique token."""
        login1 = LoginRequest(user_id="S001", role="student")
        login2 = LoginRequest(user_id="S002", role="student")
        
        response1 = AuthService.create_session(db_session, login1)
        response2 = AuthService.create_session(db_session, login2)
        
        assert response1.token != response2.token


class TestValidateSession:
    """Test session validation."""
    
    def test_validates_existing_non_expired_session(self, db_session):
        """Should validate valid non-expired session."""
        login_request = LoginRequest(user_id="S001", role="student")
        session_response = AuthService.create_session(db_session, login_request)
        
        validated = AuthService.validate_session(db_session, session_response.token)
        
        assert validated is not None
        assert validated.user_id == "S001"
        assert validated.role == "student"
    
    def test_returns_none_for_nonexistent_token(self, db_session):
        """Should return None for token that doesn't exist."""
        validated = AuthService.validate_session(db_session, "nonexistent-token")
        
        assert validated is None
    
    def test_returns_none_and_deletes_expired_session(self, db_session):
        """Should return None and delete expired session."""
        # Create session with 0 hour expiry (immediately expired)
        login_request = LoginRequest(user_id="S001", role="student")
        
        # Manually create expired session
        token = AuthService.generate_session_token()
        expired_session = Session(
            user_id="S001",
            role="student",
            token=token,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)  # Expired 1 hour ago
        )
        db_session.add(expired_session)
        db_session.commit()
        
        # Try to validate
        validated = AuthService.validate_session(db_session, token)
        
        assert validated is None
        
        # Verify session was deleted
        deleted = db_session.query(Session).filter(Session.token == token).first()
        assert deleted is None
    
    def test_validates_session_expiring_soon(self, db_session):
        """Should validate session that expires soon but not yet."""
        # Create session expiring in 1 minute
        token = AuthService.generate_session_token()
        soon_expiring_session = Session(
            user_id="S001",
            role="student",
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=1)
        )
        db_session.add(soon_expiring_session)
        db_session.commit()
        
        validated = AuthService.validate_session(db_session, token)
        
        assert validated is not None
        assert validated.user_id == "S001"


class TestInvalidateSession:
    """Test session invalidation (logout)."""
    
    def test_invalidates_existing_session(self, db_session):
        """Should delete existing session."""
        login_request = LoginRequest(user_id="S001", role="student")
        session_response = AuthService.create_session(db_session, login_request)
        
        success = AuthService.invalidate_session(db_session, session_response.token)
        
        assert success is True
        
        # Verify session was deleted
        deleted = db_session.query(Session).filter(
            Session.token == session_response.token
        ).first()
        assert deleted is None
    
    def test_returns_false_for_nonexistent_token(self, db_session):
        """Should return False for token that doesn't exist."""
        success = AuthService.invalidate_session(db_session, "nonexistent-token")
        
        assert success is False
    
    def test_can_invalidate_expired_session(self, db_session):
        """Should be able to delete expired session."""
        # Create expired session
        token = AuthService.generate_session_token()
        expired_session = Session(
            user_id="S001",
            role="student",
            token=token,
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        db_session.add(expired_session)
        db_session.commit()
        
        success = AuthService.invalidate_session(db_session, token)
        
        assert success is True


class TestGetSessionByUserId:
    """Test getting session by user ID."""
    
    def test_gets_active_session_for_user(self, db_session):
        """Should retrieve active session for user."""
        login_request = LoginRequest(user_id="S001", role="student")
        session_response = AuthService.create_session(db_session, login_request)
        
        retrieved = AuthService.get_session_by_user_id(db_session, "S001")
        
        assert retrieved is not None
        assert retrieved.user_id == "S001"
        assert retrieved.token == session_response.token
    
    def test_returns_none_for_user_without_session(self, db_session):
        """Should return None for user without active session."""
        retrieved = AuthService.get_session_by_user_id(db_session, "S999")
        
        assert retrieved is None
    
    def test_returns_none_for_user_with_expired_session(self, db_session):
        """Should return None when user's session is expired."""
        # Create expired session
        expired_session = Session(
            user_id="S001",
            role="student",
            token=AuthService.generate_session_token(),
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
        )
        db_session.add(expired_session)
        db_session.commit()
        
        retrieved = AuthService.get_session_by_user_id(db_session, "S001")
        
        assert retrieved is None
    
    def test_returns_most_recent_when_multiple_sessions(self, db_session):
        """Should return most recently created session if multiple exist."""
        # Create two sessions for same user (though this shouldn't happen in practice)
        session1 = Session(
            user_id="S001",
            role="student",
            token=AuthService.generate_session_token(),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        db_session.add(session1)
        db_session.commit()
        
        session2 = Session(
            user_id="S001",
            role="student",
            token=AuthService.generate_session_token(),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )
        db_session.add(session2)
        db_session.commit()
        
        retrieved = AuthService.get_session_by_user_id(db_session, "S001")
        
        assert retrieved is not None
        assert retrieved.user_id == "S001"

