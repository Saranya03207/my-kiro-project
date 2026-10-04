"""
Order routes for Smart Canteen Manager.
Handles order creation and management for students.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session as DBSession
from typing import List, Optional
from datetime import date
from backend.database import get_db
from backend.schemas.order import OrderCreate, OrderResponse
from backend.services.order_service import OrderService
from backend.middleware.auth_middleware import require_auth
from backend.models.session import Session


router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.get("/history", response_model=List[OrderResponse])
def get_order_history(
    status: Optional[str] = Query(None, description="Filter by order status"),
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_auth)
) -> List[OrderResponse]:
    """
    Get order history for the authenticated student.
    
    Args:
        status: Optional status filter
        db: Database session
        session: Current authenticated session
        
    Returns:
        List of orders for the student
        
    Raises:
        HTTPException: 403 if admin tries to use this endpoint
    """
    # Only students can use this endpoint (admins use /admin/orders)
    if session.role != 'student':
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "STUDENT_ONLY",
                    "message": "Students only. Admins should use /admin/orders"
                }
            }
        )
    
    try:
        orders = OrderService.get_orders_by_student(
            db, 
            session.user_id, 
            status=status
        )
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "HISTORY_FETCH_ERROR",
                    "message": f"Failed to fetch order history: {str(e)}"
                }
            }
        )


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(
    order_data: OrderCreate,
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_auth)
) -> OrderResponse:
    """
    Create a new order (booking) for the authenticated student.
    
    Args:
        order_data: Order creation data with items and quantities
        db: Database session
        session: Current authenticated session
        
    Returns:
        Created order details
        
    Raises:
        HTTPException: 400 if validation fails or items unavailable
        HTTPException: 403 if admin tries to place order
    """
    # Only students can place orders
    if session.role != 'student':
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "STUDENT_ONLY",
                    "message": "Only students can place orders"
                }
            }
        )
    
    try:
        order = OrderService.create_order(db, session.user_id, order_data)
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "ORDER_VALIDATION_ERROR",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "ORDER_CREATION_ERROR",
                    "message": f"Failed to create order: {str(e)}"
                }
            }
        )


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: DBSession = Depends(get_db),
    session: Session = Depends(require_auth)
) -> OrderResponse:
    """
    Get order details by ID.
    
    Students can only access their own orders.
    Admins can access any order.
    
    Args:
        order_id: Order ID
        db: Database session
        session: Current authenticated session
        
    Returns:
        Order details
        
    Raises:
        HTTPException: 404 if order not found
        HTTPException: 403 if student tries to access other's order
    """
    try:
        order = OrderService.get_order_by_id(db, order_id)
        
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
        
        # Students can only access their own orders
        if session.role == 'student' and order.student_id != session.user_id:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": {
                        "code": "ACCESS_DENIED",
                        "message": "You can only access your own orders"
                    }
                }
            )
        
        return order
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "ORDER_FETCH_ERROR",
                    "message": f"Failed to fetch order: {str(e)}"
                }
            }
        )