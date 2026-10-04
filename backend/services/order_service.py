"""
Order service for Smart Canteen Manager.
Handles order creation, management, and status tracking with stock validation.
"""
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.exc import SQLAlchemyError
from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.models.menu_item import MenuItem
from backend.schemas.order import OrderCreate, OrderItemCreate, OrderResponse, OrderItemResponse
from backend.services.inventory_service import InventoryService


class OrderService:
    """
    Service class for order management and processing.
    
    Responsibilities:
    - Create orders with validation and stock management
    - Retrieve and filter orders by student or status
    - Manage order status transitions
    - Calculate order totals
    - Validate menu item availability and stock
    """
    
    # Valid order status values
    VALID_STATUSES = {"pending", "preparing", "ready", "completed", "cancelled"}
    
    # Valid status transitions: current_status -> list of allowed next statuses
    VALID_TRANSITIONS = {
        "pending": {"preparing", "cancelled"},
        "preparing": {"ready", "cancelled"},
        "ready": {"completed", "cancelled"},
        "completed": set(),  # Terminal state
        "cancelled": set()   # Terminal state
    }
    
    @staticmethod
    def create_order(
        db: DBSession,
        student_id: str,
        order_data: OrderCreate
    ) -> Order:
        """
        Create a new order with validation and stock decrement.
        
        Validates that:
        - All menu items exist and are not deleted
        - All menu items are available for ordering
        - Sufficient stock exists for each item
        
        On success:
        - Creates Order and OrderItem records
        - Decrements stock for each ordered item
        
        Args:
            db: Database session
            student_id: ID of student placing order
            order_data: Order creation data with items
            
        Returns:
            Created Order object with items populated
            
        Raises:
            ValueError: If validation fails (unavailable item, insufficient stock, etc.)
        """
        try:
            # Validate all items first
            OrderService.validate_order_items(db, order_data.items)
            
            # Calculate total price
            total_price = OrderService.calculate_order_total(db, order_data.items)
            
            # Create order
            order = Order(
                student_id=student_id,
                total_price=total_price,
                status="pending"
            )
            db.add(order)
            db.flush()  # Get order ID without committing
            
            # Create order items and decrement stock
            for item_data in order_data.items:
                menu_item = db.query(MenuItem).filter(
                    MenuItem.id == item_data.menu_item_id,
                    MenuItem.is_deleted == False
                ).first()
                
                # Decrement stock
                InventoryService.decrement_stock(
                    db,
                    menu_item.id,
                    item_data.quantity
                )
                
                # Create order item
                order_item = OrderItem(
                    order_id=order.id,
                    menu_item_id=menu_item.id,
                    quantity=item_data.quantity,
                    price_at_order_time=menu_item.price
                )
                db.add(order_item)
            
            # Commit transaction
            db.commit()
            db.refresh(order)
            return order
            
        except (ValueError, SQLAlchemyError) as e:
            db.rollback()
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to create order: {str(e)}")
    
    @staticmethod
    def get_order_by_id(db: DBSession, order_id: int) -> Optional[Order]:
        """
        Get an order by ID with all associated items.
        
        Args:
            db: Database session
            order_id: Order ID
            
        Returns:
            Order if found, None otherwise
        """
        return db.query(Order).filter(Order.id == order_id).first()
    
    @staticmethod
    def get_orders_by_student(
        db: DBSession,
        student_id: str,
        status: Optional[str] = None
    ) -> List[Order]:
        """
        Get all orders placed by a specific student.
        
        Optionally filter by status.
        
        Args:
            db: Database session
            student_id: Student ID
            status: Optional status filter
            
        Returns:
            List of orders for the student
        """
        query = db.query(Order).filter(Order.student_id == student_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        return query.order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def get_all_orders(
        db: DBSession,
        status: Optional[str] = None
    ) -> List[Order]:
        """
        Get all orders with optional status filtering.
        
        Args:
            db: Database session
            status: Optional status filter
            
        Returns:
            List of all orders
        """
        query = db.query(Order)
        
        if status:
            if status not in OrderService.VALID_STATUSES:
                raise ValueError(f"Invalid status: {status}")
            query = query.filter(Order.status == status)
        
        return query.order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def update_order_status(
        db: DBSession,
        order_id: int,
        new_status: str
    ) -> Optional[Order]:
        """
        Update order status with transition validation.
        
        Only allows valid status transitions:
        - pending → preparing, cancelled
        - preparing → ready, cancelled
        - ready → completed, cancelled
        - completed, cancelled → (no transitions allowed)
        
        Args:
            db: Database session
            order_id: Order ID
            new_status: New status value
            
        Returns:
            Updated order if found and transition valid, None if not found
            
        Raises:
            ValueError: If status is invalid or transition not allowed
        """
        if new_status not in OrderService.VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")
        
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            return None
        
        # Check if transition is valid
        allowed_transitions = OrderService.VALID_TRANSITIONS.get(order.status, set())
        if new_status not in allowed_transitions:
            raise ValueError(
                f"Invalid status transition: {order.status} → {new_status}"
            )
        
        order.status = new_status
        db.commit()
        db.refresh(order)
        return order
    
    @staticmethod
    def validate_order_items(
        db: DBSession,
        items: List[OrderItemCreate]
    ) -> None:
        """
        Validate that all items in an order are available and have sufficient stock.
        
        Args:
            db: Database session
            items: List of order items to validate
            
        Raises:
            ValueError: If any item is invalid, unavailable, or out of stock
        """
        for item_data in items:
            # Check if item exists
            menu_item = db.query(MenuItem).filter(
                MenuItem.id == item_data.menu_item_id,
                MenuItem.is_deleted == False
            ).first()
            
            if not menu_item:
                raise ValueError(
                    f"Menu item {item_data.menu_item_id} not found"
                )
            
            # Check if item is available
            if not menu_item.is_available:
                raise ValueError(
                    f"Menu item '{menu_item.name}' is not available for ordering"
                )
            
            # Check stock availability
            if not InventoryService.check_stock_availability(
                db,
                menu_item.id,
                item_data.quantity
            ):
                raise ValueError(
                    f"Insufficient stock for '{menu_item.name}': "
                    f"requested={item_data.quantity}, available={menu_item.stock_quantity}"
                )
    
    @staticmethod
    def calculate_order_total(
        db: DBSession,
        items: List[OrderItemCreate]
    ) -> Decimal:
        """
        Calculate total price for an order.
        
        Sums (price * quantity) for all items in the order.
        
        Args:
            db: Database session
            items: List of order items
            
        Returns:
            Total order price as Decimal
            
        Raises:
            ValueError: If any item not found
        """
        total = Decimal("0.00")
        
        for item_data in items:
            menu_item = db.query(MenuItem).filter(
                MenuItem.id == item_data.menu_item_id
            ).first()
            
            if not menu_item:
                raise ValueError(
                    f"Menu item {item_data.menu_item_id} not found"
                )
            
            item_total = menu_item.price * item_data.quantity
            total += item_total
        
        return total
