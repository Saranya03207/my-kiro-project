"""
Authentication middleware for Smart Canteen Manager.
Handles session token validation and role-based authorization.
"""
from typing import Optional, List
from fastapi import HTTPException, Depends, Header
from sqlalchemy.orm import Session as DBSession
from backend.database import get_db
from backend.services.auth_service import AuthService
from backend.models.session import Session


def extract_token(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract session token from Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        Session token
        
    Raises:
        HTTPException: 401 if header is missing or invalid format
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Authorization header required"
                }
            }
        )
    
    # Expected format: "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_AUTH_FORMAT",
                    "message": "Invalid authorization header format. Expected: Bearer <token>"
                }
            }
        )
    
    return parts[1]


def get_current_session(
    token: str = Depends(extract_token),
    db: DBSession = Depends(get_db)
) -> Session:
    """
    Get and validate current session from token.
    
    Args:
        token: Session token extracted from header
        db: Database session
        
    Returns:
        Validated Session object
        
    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    session = AuthService.validate_session(db, token)
    
    if not session:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "INVALID_SESSION",
                    "message": "Invalid or expired session token"
                }
            }
        )
    
    return session


def require_roles(allowed_roles: List[str]):
    """
    Decorator factory for role-based authorization.
    
    Args:
        allowed_roles: List of roles allowed to access the endpoint
        
    Returns:
        Dependency function that validates user role
        
    Example:
        @router.get("/admin/orders", dependencies=[Depends(require_roles(["admin"]))])
        def get_all_orders():
            ...
    """
    def role_checker(session: Session = Depends(get_current_session)) -> Session:
        """
        Check if current session has required role.
        
        Args:
            session: Current validated session
            
        Returns:
            Session object if role is allowed
            
        Raises:
            HTTPException: 403 if user doesn't have required role
        """
        if session.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": f"Access denied. Required role: {', '.join(allowed_roles)}"
                    }
                }
            )
        
        return session
    
    return role_checker


def require_admin(session: Session = Depends(get_current_session)) -> Session:
    """
    Require admin role for endpoint access.
    
    Args:
        session: Current validated session
        
    Returns:
        Session object if user is admin
        
    Raises:
        HTTPException: 403 if user is not admin
    """
    if session.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "ADMIN_ACCESS_REQUIRED",
                    "message": "Admin access required"
                }
            }
        )
    
    return session


def require_auth(session: Session = Depends(get_current_session)) -> Session:
    """
    Require any authenticated user (student or admin).
    
    Args:
        session: Current validated session
        
    Returns:
        Session object for any authenticated user
    """
    return session
