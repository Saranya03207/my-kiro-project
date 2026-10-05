"""
Admin routes for Smart Canteen Manager.
Handles admin-only functionality: menu management, inventory, and analytics.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session as DBSession
from typing import List, Dict, Any, Optional
from datetime import date, datetime, timedelta
from decimal import Decimal
import os
import uuid
import re
from backend.database import get_db
from backend.schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from backend.schemas.order import OrderResponse
from backend.services.menu_service import MenuService
from backend.services.inventory_service import InventoryService
from backend.services.analytics_service import AnalyticsService
from backend.services.order_service import OrderService
from backend.middleware.auth_middleware import require_admin
from backend.models.session import Session


router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


# Menu Management Routes
@router.post("/menu/upload-image", status_code=200)
async def upload_food_image(
    file: UploadFile = File(...),
    session: Session = Depends(require_admin)
) -> dict:
    """
    Upload a food image for a menu item (admin only).
    Accepts PNG, JPEG, WebP up to 5MB.
    Stores file under frontend/assets/food/.

    Returns:
        dict: {"image_url": "assets/food/<filename>"}
    """
    allowed_content_types = {"image/png", "image/jpeg", "image/webp"}
    allowed_extensions = {".png", ".jpg", ".jpeg", ".webp"}

    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()

    if file.content_type not in allowed_content_types or ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_IMAGE_TYPE",
                    "message": "Invalid file type. Allowed formats: PNG, JPEG, WebP"
                }
            }
        )

    max_size = 5 * 1024 * 1024  # 5MB
    content = await file.read()

    if len(content) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "EMPTY_FILE",
                    "message": "Uploaded file is empty"
                }
            }
        )

    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": "File size exceeds maximum limit of 5MB"
                }
            }
        )

    upload_dir = os.path.join("frontend", "assets", "food")
    os.makedirs(upload_dir, exist_ok=True)

    clean_base = re.sub(r'[^a-zA-Z0-9_-]', '_', os.path.splitext(filename)[0])[:30]
    unique_filename = f"upload_{uuid.uuid4().hex[:8]}_{clean_base}{ext}"
    dest_path = os.path.join(upload_dir, unique_filename)

    with open(dest_path, "wb") as f:
        f.write(content)

    relative_url = f"assets/food/{unique_filename}"
    return {"image_url": relative_url}


@router.post("/menu/items", response_model=MenuItemResponse, status_code=201)
def create_menu_item(
    item_data: MenuItemCreate,
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> MenuItemResponse:
    """
    Create a new menu item (admin only).

    Args:
        item_data: Menu item creation data
        db: Database session
        session: Current admin session

    Returns:
        Created menu item details

    Raises:
        HTTPException: 400 if validation fails or name already exists
    """
    try:
        item = MenuService.create_menu_item(db, item_data)
        return item
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "MENU_ITEM_VALIDATION_ERROR",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "MENU_ITEM_CREATION_ERROR",
                    "message": f"Failed to create menu item: {str(e)}"
                }
            }
        )


@router.put("/menu/items/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    item_data: MenuItemUpdate,
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> MenuItemResponse:
    """
    Update an existing menu item (admin only).

    Args:
        item_id: Menu item ID
        item_data: Menu item update data
        db: Database session
        session: Current admin session

    Returns:
        Updated menu item details

    Raises:
        HTTPException: 404 if item not found
        HTTPException: 400 if validation fails
    """
    try:
        item = MenuService.update_menu_item(db, item_id, item_data)

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

        return item
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "MENU_ITEM_VALIDATION_ERROR",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "MENU_ITEM_UPDATE_ERROR",
                    "message": f"Failed to update menu item: {str(e)}"
                }
            }
        )


@router.patch("/menu/items/{item_id}/availability", response_model=MenuItemResponse)
def toggle_menu_item_availability(
    item_id: int,
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> MenuItemResponse:
    """
    Toggle menu item availability (admin only).

    Args:
        item_id: Menu item ID
        db: Database session
        session: Current admin session

    Returns:
        Updated menu item details

    Raises:
        HTTPException: 404 if item not found
    """
    try:
        item = MenuService.toggle_availability(db, item_id)

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

        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "AVAILABILITY_UPDATE_ERROR",
                    "message": f"Failed to update availability: {str(e)}"
                }
            }
        )


@router.delete("/menu/items/{item_id}", status_code=204)
def delete_menu_item(
    item_id: int,
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> None:
    """
    Soft delete a menu item (admin only).

    Args:
        item_id: Menu item ID
        db: Database session
        session: Current admin session

    Returns:
        No content (204)

    Raises:
        HTTPException: 404 if item not found
    """
    try:
        success = MenuService.delete_menu_item(db, item_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "ITEM_NOT_FOUND",
                        "message": f"Menu item with ID {item_id} not found"
                    }
                }
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "DELETE_ERROR",
                    "message": f"Failed to delete menu item: {str(e)}"
                }
            }
        )


# Inventory Management Routes
@router.get("/inventory")
def get_inventory(
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> List[Dict[str, Any]]:
    """
    Get all inventory stock levels (admin only).

    Args:
        db: Database session
        session: Current admin session

    Returns:
        List of inventory items with stock information
    """
    try:
        inventory = InventoryService.get_inventory(db)
        return [
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "stock_quantity": item.stock_quantity,
                "stock_threshold": item.stock_threshold,
                "is_low_stock": item.stock_quantity <= item.stock_threshold,
                "is_available": item.is_available
            }
            for item in inventory
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "INVENTORY_FETCH_ERROR",
                    "message": f"Failed to fetch inventory: {str(e)}"
                }
            }
        )


@router.put("/inventory/{item_id}")
def update_stock_quantity(
    item_id: int,
    quantity: int = Query(..., ge=0, description="New stock quantity"),
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Update stock quantity for a menu item (admin only).

    Args:
        item_id: Menu item ID
        new_quantity: New stock quantity
        db: Database session
        session: Current admin session

    Returns:
        Updated stock information

    Raises:
        HTTPException: 404 if item not found
        HTTPException: 400 if quantity is negative
    """
    try:
        if quantity < 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_QUANTITY",
                        "message": "Stock quantity cannot be negative"
                    }
                }
            )

        item = InventoryService.update_stock(db, item_id, quantity)

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

        return {
            "id": item.id,
            "name": item.name,
            "stock_quantity": item.stock_quantity,
            "stock_threshold": item.stock_threshold,
            "is_low_stock": item.stock_quantity <= item.stock_threshold,
            "message": f"Stock updated to {quantity}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "STOCK_UPDATE_ERROR",
                    "message": f"Failed to update stock: {str(e)}"
                }
            }
        )


@router.get("/inventory/low-stock")
def get_low_stock_items(
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> List[Dict[str, Any]]:
    """
    Get items with low stock (admin only).

    Args:
        db: Database session
        session: Current admin session

    Returns:
        List of items below their stock threshold
    """
    try:
        low_stock_items = InventoryService.get_low_stock_items(db)
        return [
            {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "stock_quantity": item.stock_quantity,
                "stock_threshold": item.stock_threshold,
                "shortage": item.stock_threshold - item.stock_quantity
            }
            for item in low_stock_items
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "LOW_STOCK_FETCH_ERROR",
                    "message": f"Failed to fetch low stock items: {str(e)}"
                }
            }
        )


@router.put("/inventory/{item_id}/threshold")
def update_stock_threshold(
    item_id: int,
    threshold: int = Query(..., ge=0, description="New stock threshold"),
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Update stock threshold for a menu item (admin only).

    Args:
        item_id: Menu item ID
        new_threshold: New stock threshold
        db: Database session
        session: Current admin session

    Returns:
        Updated threshold information

    Raises:
        HTTPException: 404 if item not found
        HTTPException: 400 if threshold is negative
    """
    try:
        if threshold < 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_THRESHOLD",
                        "message": "Stock threshold cannot be negative"
                    }
                }
            )

        item = InventoryService.update_stock_threshold(db, item_id, threshold)

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

        return {
            "id": item.id,
            "name": item.name,
            "stock_quantity": item.stock_quantity,
            "stock_threshold": item.stock_threshold,
            "is_low_stock": item.stock_quantity <= item.stock_threshold,
            "message": f"Stock threshold updated to {threshold}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "THRESHOLD_UPDATE_ERROR",
                    "message": f"Failed to update threshold: {str(e)}"
                }
            }
        )


# Order Management Routes
@router.get("/orders", response_model=List[OrderResponse])
def get_all_orders(
    status: Optional[str] = Query(None, description="Filter by order status"),
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> List[OrderResponse]:
    """
    Get all orders with optional filtering (admin only).

    Args:
        status: Optional status filter
        db: Database session
        session: Current admin session

    Returns:
        List of all orders matching filters
    """
    try:
        orders = OrderService.get_all_orders(
            db,
            status=status
        )
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "ORDERS_FETCH_ERROR",
                    "message": f"Failed to fetch orders: {str(e)}"
                }
            }
        )


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    new_status: str = Query(..., description="New status: pending, preparing, ready, completed, cancelled"),
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> OrderResponse:
    """
    Update order status (admin only).

    Args:
        order_id: Order ID
        new_status: New order status
        db: Database session
        session: Current admin session

    Returns:
        Updated order details

    Raises:
        HTTPException: 404 if order not found
        HTTPException: 400 if invalid status transition
    """
    try:
        # Validate status value
        valid_statuses = ['pending', 'preparing', 'ready', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_STATUS",
                        "message": f"Invalid status. Valid options: {', '.join(valid_statuses)}"
                    }
                }
            )

        order = OrderService.update_order_status(db, order_id, new_status)

        if not order:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": {
                        "code": "ORDER_NOT_FOUND",
                        "message": f"Order with ID {order_id} not found"
                    }
                }
            )

        return order
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "STATUS_UPDATE_ERROR",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "UPDATE_ERROR",
                    "message": f"Failed to update order status: {str(e)}"
                }
            }
        )


# Analytics Routes
@router.get("/analytics/sales/daily")
def get_daily_sales(
    target_date: Optional[date] = Query(None, description="Target date (defaults to today)"),
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get daily sales statistics (admin only).

    Args:
        target_date: Date to get sales for (defaults to today)
        db: Database session
        session: Current admin session

    Returns:
        Daily sales statistics
    """
    try:
        sales_data = AnalyticsService.get_daily_sales(db, target_date)
        return sales_data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "SALES_FETCH_ERROR",
                    "message": f"Failed to fetch daily sales: {str(e)}"
                }
            }
        )


@router.get("/analytics/sales/range")
def get_sales_by_date_range(
    start_date: date = Query(..., description="Start date (inclusive)"),
    end_date: date = Query(..., description="End date (inclusive)"),
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> List[Dict[str, Any]]:
    """
    Get sales statistics for a date range (admin only).

    Args:
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        db: Database session
        session: Current admin session

    Returns:
        List of daily sales statistics for the date range

    Raises:
        HTTPException: 400 if date range is invalid
    """
    try:
        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "INVALID_DATE_RANGE",
                        "message": "Start date must be before or equal to end date"
                    }
                }
            )

        # Limit range to 90 days to prevent excessive queries
        if (end_date - start_date).days > 90:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "DATE_RANGE_TOO_LARGE",
                        "message": "Date range cannot exceed 90 days"
                    }
                }
            )

        sales_data = AnalyticsService.get_sales_by_date_range(db, start_date, end_date)
        return sales_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "SALES_RANGE_FETCH_ERROR",
                    "message": f"Failed to fetch sales range: {str(e)}"
                }
            }
        )


@router.get("/analytics/popular-items")
def get_popular_items(
    days: int = Query(7, ge=1, le=90, description="Number of days to look back (1-90)"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of items to return (1-50)"),
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_admin)
) -> List[Dict[str, Any]]:
    """
    Get most popular menu items (admin only).

    Args:
        days: Number of days to look back (1-90)
        limit: Maximum number of items to return (1-50)
        db: Database session
        session: Current admin session

    Returns:
        List of popular items with popularity scores
    """
    try:
        popular_items = AnalyticsService.get_popular_items(db, days, limit)
        return popular_items
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "POPULAR_ITEMS_FETCH_ERROR",
                    "message": f"Failed to fetch popular items: {str(e)}"
                }
            }
        )
