"""
Menu routes for Smart Canteen Manager.
Handles menu item viewing for students.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as DBSession
from typing import List, Optional
from backend.database import get_db
from backend.schemas.menu_item import MenuItemResponse
from backend.services.menu_service import MenuService
from backend.middleware.auth_middleware import require_auth
from backend.models.session import Session


router = APIRouter(prefix="/api/v1/menu", tags=["menu"])


@router.get("/items", response_model=List[MenuItemResponse])
def get_menu_items(
    search: Optional[str] = Query(None, description="Search in item name and description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_auth)
) -> List[MenuItemResponse]:
    """
    Get all available menu items with optional search and category filtering.
    
    Only returns items that are available and not deleted.
    Students can search by name/description and filter by category.
    
    Args:
        search: Optional search query for name and description
        category: Optional category filter
        db: Database session
        session: Current authenticated session
        
    Returns:
        List of available menu items matching the filters
    """
    try:
        if search or category:
            # Use search functionality with filters
            items = MenuService.search_menu_items(db, search=search, category=category)
        else:
            # Get all available items
            items = MenuService.get_available_menu_items(db)
        
        return items
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "MENU_FETCH_ERROR",
                    "message": f"Failed to fetch menu items: {str(e)}"
                }
            }
        )


@router.get("/items/{item_id}", response_model=MenuItemResponse)
def get_menu_item(
    item_id: int,
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_auth)
) -> MenuItemResponse:
    """
    Get details of a specific menu item by ID.
    
    Args:
        item_id: Menu item ID
        db: Database session
        session: Current authenticated session
        
    Returns:
        Menu item details
        
    Raises:
        HTTPException: 404 if item not found or not available
    """
    try:
        item = MenuService.get_menu_item_by_id(db, item_id)
        
        if not item:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "ITEM_NOT_FOUND",
                        "message": f"Menu item with ID {item_id} not found"
                    }
                }
            )
        
        # Only return available items to students
        if not item.is_available or item.is_deleted:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "ITEM_NOT_AVAILABLE",
                        "message": f"Menu item with ID {item_id} is not available"
                    }
                }
            )
        
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "ITEM_FETCH_ERROR",
                    "message": f"Failed to fetch menu item: {str(e)}"
                }
            }
        )