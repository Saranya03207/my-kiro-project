"""
Service layer modules for Smart Canteen Manager.
Contains business logic separated from route handlers.
"""
from backend.services.auth_service import AuthService
from backend.services.menu_service import MenuService

__all__ = ["AuthService", "MenuService"]
