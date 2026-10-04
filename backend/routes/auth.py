"""
Authentication routes for Smart Canteen Manager.
Handles login and logout endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from backend.database import get_db
from backend.schemas.auth import LoginRequest, SessionResponse
from backend.services.auth_service import AuthService
from backend.middleware.auth_middleware import extract_token


router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/login", response_model=SessionResponse, status_code=200)
def login(
    login_request: LoginRequest,
    db: DBSession = Depends(get_db)
) -> SessionResponse:
    """
    Create a new user session (login).
    
    Args:
        login_request: User credentials (user_id and role)
        db: Database session
        
    Returns:
        SessionResponse with token and session details
        
    Raises:
        HTTPException: 400 if validation fails
    """
    try:
        session_response = AuthService.create_session(db, login_request)
        return session_response
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "LOGIN_FAILED",
                    "message": str(e)
                }
            }
        )


@router.post("/logout", status_code=200)
def logout(
    token: str = Depends(extract_token),
    db: DBSession = Depends(get_db)
) -> dict:
    """
    Invalidate current session (logout).
    
    Args:
        token: Session token from Authorization header
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 401 if token is invalid
        HTTPException: 404 if session not found
    """
    success = AuthService.invalidate_session(db, token)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "SESSION_NOT_FOUND",
                    "message": "Session not found or already logged out"
                }
            }
        )
    
    return {"message": "Logged out successfully"}
