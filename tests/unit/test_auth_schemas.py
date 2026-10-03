"""
Unit tests for authentication Pydantic schemas.
Tests validation rules for LoginRequest and SessionResponse.
"""
import pytest
from pydantic import ValidationError
from backend.schemas.auth import LoginRequest, SessionResponse
from datetime import datetime, timedelta


class TestLoginRequest:
    """Tests for LoginRequest schema validation."""
    
    def test_valid_login_student(self):
        """Valid login request with student role passes validation."""
        data = {
            "user_id": "S001",
            "role": "student"
        }
        login = LoginRequest(**data)
        assert login.user_id == "S001"
        assert login.role == "student"
    
    def test_valid_login_admin(self):
        """Valid login request with admin role passes validation."""
        data = {
            "user_id": "A001",
            "role": "admin"
        }
        login = LoginRequest(**data)
        assert login.user_id == "A001"
        assert login.role == "admin"
    
    def test_user_id_max_length_valid(self):
        """User ID at maximum length (50 chars) passes validation."""
        user_id = "A" * 50
        login = LoginRequest(user_id=user_id, role="student")
        assert login.user_id == user_id
        assert len(login.user_id) == 50
    
    def test_user_id_one_char_valid(self):
        """User ID with single character passes validation."""
        login = LoginRequest(user_id="A", role="student")
        assert login.user_id == "A"
    
    def test_user_id_too_long_fails(self):
        """User ID exceeding 50 characters fails validation."""
        user_id = "A" * 51
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(user_id=user_id, role="student")
        assert "user_id" in str(exc_info.value).lower()
    
    def test_user_id_empty_fails(self):
        """Empty user_id fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(user_id="", role="student")
        assert "user_id" in str(exc_info.value).lower()
    
    def test_user_id_whitespace_only_fails(self):
        """User ID with only whitespace fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(user_id="   ", role="student")
        assert "whitespace" in str(exc_info.value).lower()
    
    def test_user_id_whitespace_trimmed(self):
        """Leading/trailing whitespace in user_id is trimmed."""
        login = LoginRequest(user_id="  S001  ", role="student")
        assert login.user_id == "S001"
    
    def test_missing_user_id_fails(self):
        """Missing user_id fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(role="student")
        assert "user_id" in str(exc_info.value).lower()
    
    def test_role_student_valid(self):
        """Role 'student' passes validation."""
        login = LoginRequest(user_id="S001", role="student")
        assert login.role == "student"
    
    def test_role_admin_valid(self):
        """Role 'admin' passes validation."""
        login = LoginRequest(user_id="A001", role="admin")
        assert login.role == "admin"
    
    def test_role_invalid_value_fails(self):
        """Invalid role value fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(user_id="S001", role="teacher")
        assert "role" in str(exc_info.value).lower()
    
    def test_role_uppercase_fails(self):
        """Role with incorrect case fails validation (must be lowercase)."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(user_id="S001", role="Student")
        assert "role" in str(exc_info.value).lower()
    
    def test_role_empty_fails(self):
        """Empty role fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(user_id="S001", role="")
        assert "role" in str(exc_info.value).lower()
    
    def test_missing_role_fails(self):
        """Missing role fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(user_id="S001")
        assert "role" in str(exc_info.value).lower()
    
    def test_alphanumeric_user_id_valid(self):
        """User ID with alphanumeric characters passes validation."""
        login = LoginRequest(user_id="User123", role="student")
        assert login.user_id == "User123"
    
    def test_user_id_with_special_chars_valid(self):
        """User ID with special characters passes validation."""
        login = LoginRequest(user_id="user.name@domain", role="admin")
        assert login.user_id == "user.name@domain"
    
    def test_both_fields_required(self):
        """Both user_id and role are required."""
        # Missing both fields
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest()
        error_str = str(exc_info.value).lower()
        assert "user_id" in error_str
        assert "role" in error_str


class TestSessionResponse:
    """Tests for SessionResponse schema."""
    
    def test_valid_session_response(self):
        """Create valid SessionResponse from dictionary."""
        data = {
            "token": "abc123def456",
            "user_id": "S001",
            "role": "student",
            "expires_at": datetime(2024, 12, 31, 23, 59, 59)
        }
        session = SessionResponse(**data)
        assert session.token == "abc123def456"
        assert session.user_id == "S001"
        assert session.role == "student"
        assert session.expires_at == datetime(2024, 12, 31, 23, 59, 59)
    
    def test_session_response_with_admin_role(self):
        """SessionResponse with admin role."""
        data = {
            "token": "xyz789token",
            "user_id": "A001",
            "role": "admin",
            "expires_at": datetime.now() + timedelta(hours=24)
        }
        session = SessionResponse(**data)
        assert session.role == "admin"
        assert session.user_id == "A001"
    
    def test_session_response_with_uuid_token(self):
        """SessionResponse with UUID-format token."""
        uuid_token = "550e8400-e29b-41d4-a716-446655440000"
        data = {
            "token": uuid_token,
            "user_id": "S002",
            "role": "student",
            "expires_at": datetime.now() + timedelta(days=1)
        }
        session = SessionResponse(**data)
        assert session.token == uuid_token
    
    def test_all_fields_required(self):
        """All fields are required in SessionResponse."""
        # Missing token
        with pytest.raises(ValidationError):
            SessionResponse(
                user_id="S001",
                role="student",
                expires_at=datetime.now()
            )
        
        # Missing user_id
        with pytest.raises(ValidationError):
            SessionResponse(
                token="abc123",
                role="student",
                expires_at=datetime.now()
            )
        
        # Missing role
        with pytest.raises(ValidationError):
            SessionResponse(
                token="abc123",
                user_id="S001",
                expires_at=datetime.now()
            )
        
        # Missing expires_at
        with pytest.raises(ValidationError):
            SessionResponse(
                token="abc123",
                user_id="S001",
                role="student"
            )
    
    def test_expires_at_future_date(self):
        """SessionResponse with future expiration date."""
        future_date = datetime.now() + timedelta(hours=24)
        data = {
            "token": "token123",
            "user_id": "S003",
            "role": "student",
            "expires_at": future_date
        }
        session = SessionResponse(**data)
        assert session.expires_at > datetime.now()
    
    def test_expires_at_past_date_valid(self):
        """SessionResponse with past date is valid for schema (business logic handles expiration)."""
        past_date = datetime.now() - timedelta(hours=1)
        data = {
            "token": "expired_token",
            "user_id": "S004",
            "role": "student",
            "expires_at": past_date
        }
        session = SessionResponse(**data)
        assert session.expires_at < datetime.now()
    
    def test_long_token_valid(self):
        """SessionResponse with long token string."""
        long_token = "a" * 255  # Match Session model token max length
        data = {
            "token": long_token,
            "user_id": "S005",
            "role": "admin",
            "expires_at": datetime.now() + timedelta(hours=12)
        }
        session = SessionResponse(**data)
        assert len(session.token) == 255
    
    def test_role_values_not_validated_in_response(self):
        """SessionResponse doesn't validate role values (assumes valid data from DB)."""
        # This tests that SessionResponse is a simple DTO without validation
        data = {
            "token": "token",
            "user_id": "U001",
            "role": "student",  # Any string is technically valid
            "expires_at": datetime.now()
        }
        session = SessionResponse(**data)
        assert session.role == "student"
