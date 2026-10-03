"""
Session model for Smart Canteen Manager.
Represents user authentication sessions.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.database import Base


class Session(Base):
    """
    Session model for user authentication.
    
    Attributes:
        id: Primary key
        user_id: User identifier
        role: User role ('student' or 'admin')
        token: Unique session token (UUID)
        created_at: Timestamp of session creation
        expires_at: Timestamp when session expires
    """
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
