"""
Pydantic schemas for authentication validation.
Handles request validation and response serialization for authentication and sessions.
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Literal


class LoginRequest(BaseModel):
    """
    Schema for user login request.
    
    Validates:
    - user_id: Required string, max 50 characters
    - role: Must be either 'student' or 'admin'
    """
    user_id: str = Field(..., min_length=1, max_length=50)
    role: Literal['student', 'admin']
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id_not_empty(cls, v: str) -> str:
        """Validate that user_id is not empty or whitespace only."""
        if not v.strip():
            raise ValueError('User ID cannot be empty or whitespace only')
        return v.strip()
    
    @field_validator('role')
    @classmethod
    def validate_role_value(cls, v: str) -> str:
        """Validate that role is either 'student' or 'admin'."""
        if v not in ['student', 'admin']:
            raise ValueError("Role must be either 'student' or 'admin'")
        return v


class SessionResponse(BaseModel):
    """
    Schema for session API responses.
    
    Returns session details including token and expiration
    after successful authentication.
    """
    token: str
    user_id: str
    role: str
    expires_at: datetime
