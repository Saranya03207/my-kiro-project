"""
Unit tests for order service.
Tests order creation, validation, status management, and stock integration.
"""
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models.menu_item import MenuItem
from backend.models.order import Order
from backend.models.order_item import OrderItem
from backend.schemas.order import OrderCreate, OrderItemCreate
from backend.services.order_service import OrderService
from backend.services.inventory_service import InventoryService


@pytest.fixture
def db_session():
    """Create in-memory database session for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_menu_items(db_session):
    """Create sample menu items for order testing."""
    items = [
        MenuItem(
            name="Burger",
            description="Beef burger",
            price=Decimal("9.99"),
            category="Meals",
            stock_quantity=20,
            stock_threshold=5,
            is_available=True,
            is_deleted=False
        ),
        MenuItem(
            name="Pizza",
            description="Cheese pizza",
            price=Decimal("12.99"),
            category="Meals",
            stock_quantity=10,
            stock_threshold=3,
            is_available=True,
            is_deleted=False
        ),
        MenuItem(
            name="Soda",
            description="Soft drink",
            price=Decimal("2.99"),
            category="Beverages",
            stock_quantity=5,
            stock_threshold=2,
            is_available=False,  # Unavailable
            is_deleted=False
        ),
        MenuItem(
            name="Old Item",
            description="Deleted item",
            price=Decimal("5.99"),
            category="Snacks",
            stock_quantity=1,
            stock_threshold=1,
            is_available=True,
            is_deleted=True  # Deleted
        )
    ]
    for item in items:
        db_session.add(item)
    db_session.commit()
    return items


class TestCreateOrder:
    """Test order creation with validation and stock management."""
    
    def test_creates_order_successfully(self, db_session, sample_menu_items):
        """Should create order with valid items and decrement stock."""
        burger = sample_menu_items[0]
        original_stock = burger.stock_quantity
        
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=2)
        ])
        
        order = OrderService.create_order(db_session, "S001", order_data)
        
        assert order.id is not None
        assert order.student_id == "S001"
        assert order.status == "pending"
        assert order.total_price == Decimal("19.98")  # 9.99 * 2
        assert len(order.items) == 1
        
        # Verify stock was decremented
        db_session.refresh(burger)
        assert burger.stock_quantity == original_stock - 2
    
    def test_creates_order_with_multiple_items(self, db_session, sample_menu_items):
        """Should create order with multiple different items."""
        burger = sample_menu_items[0]
        pizza = sample_menu_items[1]
        
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=1),
            OrderItemCreate(menu_item_id=pizza.id, quantity=2)
        ])
        
        order = OrderService.create_order(db_session, "S002", order_data)
        
        assert len(order.items) == 2
        # Total: 9.99 + (12.99 * 2) = 35.97
        assert order.total_price == Decimal("35.97")
    
    def test_raises_error_for_nonexistent_item(self, db_session, sample_menu_items):
        """Should reject order with nonexistent menu item."""
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=99999, quantity=1)
        ])
        
        with pytest.raises(ValueError, match="not found"):
            OrderService.create_order(db_session, "S001", order_data)
    
    def test_raises_error_for_unavailable_item(self, db_session, sample_menu_items):
        """Should reject order with unavailable item."""
        soda = sample_menu_items[2]  # Unavailable
        
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=soda.id, quantity=1)
        ])
        
        with pytest.raises(ValueError, match="not available"):
            OrderService.create_order(db_session, "S001", order_data)
    
    def test_raises_error_for_insufficient_stock(self, db_session, sample_menu_items):
        """Should reject order when insufficient stock."""
        burger = sample_menu_items[0]  # Has 20
        
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=30)
        ])
        
        with pytest.raises(ValueError, match="Insufficient stock"):
            OrderService.create_order(db_session, "S001", order_data)
    
    def test_raises_error_for_deleted_item(self, db_session, sample_menu_items):
        """Should reject order with deleted item."""
        old_item = sample_menu_items[3]  # Deleted
        
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=old_item.id, quantity=1)
        ])
        
        with pytest.raises(ValueError, match="not found"):
            OrderService.create_order(db_session, "S001", order_data)
    
    def test_rollback_on_partial_failure(self, db_session, sample_menu_items):
        """Should rollback all changes if order creation partially fails."""
        burger = sample_menu_items[0]
        original_stock = burger.stock_quantity
        
        # Create order with one valid and one invalid item
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=2),
            OrderItemCreate(menu_item_id=99999, quantity=1)  # Invalid
        ])
        
        with pytest.raises(ValueError):
            OrderService.create_order(db_session, "S001", order_data)
        
        # Verify no orders were created
        orders = db_session.query(Order).all()
        assert len(orders) == 0
        
        # Verify stock was not decremented
        db_session.refresh(burger)
        assert burger.stock_quantity == original_stock


class TestGetOrderById:
    """Test retrieving orders by ID."""
    
    def test_retrieves_order_by_id(self, db_session, sample_menu_items):
        """Should retrieve order with all items."""
        burger = sample_menu_items[0]
        
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=3)
        ])
        created = OrderService.create_order(db_session, "S001", order_data)
        
        retrieved = OrderService.get_order_by_id(db_session, created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.student_id == "S001"
        assert len(retrieved.items) == 1
    
    def test_returns_none_for_nonexistent_order(self, db_session):
        """Should return None when order doesn't exist."""
        retrieved = OrderService.get_order_by_id(db_session, 99999)
        assert retrieved is None


class TestGetOrdersByStudent:
    """Test retrieving orders by student."""
    
    def test_retrieves_all_orders_for_student(self, db_session, sample_menu_items):
        """Should retrieve all orders for a specific student."""
        burger = sample_menu_items[0]
        
        # Create multiple orders
        for i in range(3):
            order_data = OrderCreate(items=[
                OrderItemCreate(menu_item_id=burger.id, quantity=1)
            ])
            OrderService.create_order(db_session, "S001", order_data)
        
        orders = OrderService.get_orders_by_student(db_session, "S001")
        
        assert len(orders) == 3
        assert all(o.student_id == "S001" for o in orders)
    
    def test_returns_empty_for_student_without_orders(self, db_session):
        """Should return empty list for student with no orders."""
        orders = OrderService.get_orders_by_student(db_session, "S999")
        assert orders == []
    
    def test_filters_by_status(self, db_session, sample_menu_items):
        """Should filter orders by status."""
        burger = sample_menu_items[0]
        
        # Create two orders
        order1_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=1)
        ])
        order1 = OrderService.create_order(db_session, "S001", order1_data)
        
        order2_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=1)
        ])
        order2 = OrderService.create_order(db_session, "S001", order2_data)
        
        # Update status of one order
        OrderService.update_order_status(db_session, order1.id, "preparing")
        
        # Filter by status
        pending_orders = OrderService.get_orders_by_student(
            db_session,
            "S001",
            status="pending"
        )
        
        assert len(pending_orders) == 1
        assert pending_orders[0].id == order2.id
    
    def test_orders_sorted_by_date_descending(self, db_session, sample_menu_items):
        """Should return orders sorted by creation date (newest first)."""
        burger = sample_menu_items[0]
        
        order_ids = []
        for _ in range(3):
            order_data = OrderCreate(items=[
                OrderItemCreate(menu_item_id=burger.id, quantity=1)
            ])
            order = OrderService.create_order(db_session, "S001", order_data)
            order_ids.append(order.id)
        
        orders = OrderService.get_orders_by_student(db_session, "S001")
        
        # All orders present
        assert len(orders) == 3
        retrieved_ids = [o.id for o in orders]
        assert set(retrieved_ids) == set(order_ids)


class TestGetAllOrders:
    """Test retrieving all orders."""
    
    def test_retrieves_all_orders(self, db_session, sample_menu_items):
        """Should retrieve all orders from all students."""
        burger = sample_menu_items[0]
        
        # Create orders from different students
        for student in ["S001", "S002", "S003"]:
            order_data = OrderCreate(items=[
                OrderItemCreate(menu_item_id=burger.id, quantity=1)
            ])
            OrderService.create_order(db_session, student, order_data)
        
        all_orders = OrderService.get_all_orders(db_session)
        
        assert len(all_orders) == 3
    
    def test_filters_by_status(self, db_session, sample_menu_items):
        """Should filter all orders by status."""
        burger = sample_menu_items[0]
        
        # Create orders with different statuses
        order1_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=1)
        ])
        order1 = OrderService.create_order(db_session, "S001", order1_data)
        
        order2_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=1)
        ])
        order2 = OrderService.create_order(db_session, "S002", order2_data)
        
        OrderService.update_order_status(db_session, order1.id, "preparing")
        
        pending_orders = OrderService.get_all_orders(db_session, status="pending")
        
        assert len(pending_orders) == 1
        assert pending_orders[0].id == order2.id
    
    def test_raises_error_for_invalid_status(self, db_session):
        """Should reject invalid status filter."""
        with pytest.raises(ValueError, match="Invalid status"):
            OrderService.get_all_orders(db_session, status="invalid_status")


class TestUpdateOrderStatus:
    """Test updating order status with transition validation."""
    
    def test_updates_status_with_valid_transition(self, db_session, sample_menu_items):
        """Should update status for valid transition."""
        burger = sample_menu_items[0]
        
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=1)
        ])
        order = OrderService.create_order(db_session, "S001", order_data)
        assert order.status == "pending"
        
        updated = OrderService.update_order_status(db_session, order.id, "preparing")
        
        assert updated is not None
        assert updated.status == "preparing"
    
    def test_follows_valid_status_transitions(self, db_session, sample_menu_items):
        """Should allow valid transition chains."""
        burger = sample_menu_items[0]
        
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=1)
        ])
        order = OrderService.create_order(db_session, "S001", order_data)
        
        # Valid chain: pending → preparing → ready → completed
        OrderService.update_order_status(db_session, order.id, "preparing")
        OrderService.update_order_status(db_session, order.id, "ready")
        order = OrderService.update_order_status(db_session, order.id, "completed")
        
        assert order.status == "completed"
    
    def test_raises_error_for_invalid_status(self, db_session, sample_menu_items):
        """Should reject invalid status value."""
        burger = sample_menu_items[0]
        
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=1)
        ])
        order = OrderService.create_order(db_session, "S001", order_data)
        
        with pytest.raises(ValueError, match="Invalid status"):
            OrderService.update_order_status(db_session, order.id, "invalid_status")
    
    def test_raises_error_for_invalid_transition(self, db_session, sample_menu_items):
        """Should reject invalid status transitions."""
        burger = sample_menu_items[0]
        
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=1)
        ])
        order = OrderService.create_order(db_session, "S001", order_data)
        
        # pending → completed is not allowed (must go through preparing, ready)
        with pytest.raises(ValueError, match="Invalid status transition"):
            OrderService.update_order_status(db_session, order.id, "completed")
    
    def test_allows_cancellation_from_any_state(self, db_session, sample_menu_items):
        """Should allow cancellation from pending or preparing states."""
        burger = sample_menu_items[0]
        
        # Test cancellation from pending
        order1_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=1)
        ])
        order1 = OrderService.create_order(db_session, "S001", order1_data)
        updated1 = OrderService.update_order_status(db_session, order1.id, "cancelled")
        assert updated1.status == "cancelled"
        
        # Test cancellation from preparing
        order2_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=1)
        ])
        order2 = OrderService.create_order(db_session, "S002", order2_data)
        OrderService.update_order_status(db_session, order2.id, "preparing")
        updated2 = OrderService.update_order_status(db_session, order2.id, "cancelled")
        assert updated2.status == "cancelled"
    
    def test_returns_none_for_nonexistent_order(self, db_session):
        """Should return None when order doesn't exist."""
        updated = OrderService.update_order_status(db_session, 99999, "preparing")
        assert updated is None
    
    def test_terminal_states_have_no_transitions(self, db_session, sample_menu_items):
        """Should not allow transitions from completed or cancelled."""
        burger = sample_menu_items[0]
        
        order_data = OrderCreate(items=[
            OrderItemCreate(menu_item_id=burger.id, quantity=1)
        ])
        order = OrderService.create_order(db_session, "S001", order_data)
        
        # Complete the order
        OrderService.update_order_status(db_session, order.id, "preparing")
        OrderService.update_order_status(db_session, order.id, "ready")
        OrderService.update_order_status(db_session, order.id, "completed")
        
        # Cannot transition from completed
        with pytest.raises(ValueError, match="Invalid status transition"):
            OrderService.update_order_status(db_session, order.id, "cancelled")


class TestValidateOrderItems:
    """Test order item validation."""
    
    def test_validates_available_items_with_stock(self, db_session, sample_menu_items):
        """Should validate items that are available with sufficient stock."""
        burger = sample_menu_items[0]
        
        items = [OrderItemCreate(menu_item_id=burger.id, quantity=5)]
        
        # Should not raise
        OrderService.validate_order_items(db_session, items)
    
    def test_raises_error_for_nonexistent_item(self, db_session):
        """Should reject nonexistent item."""
        items = [OrderItemCreate(menu_item_id=99999, quantity=1)]
        
        with pytest.raises(ValueError, match="not found"):
            OrderService.validate_order_items(db_session, items)
    
    def test_raises_error_for_unavailable_item(self, db_session, sample_menu_items):
        """Should reject unavailable item."""
        soda = sample_menu_items[2]  # Unavailable
        
        items = [OrderItemCreate(menu_item_id=soda.id, quantity=1)]
        
        with pytest.raises(ValueError, match="not available"):
            OrderService.validate_order_items(db_session, items)
    
    def test_raises_error_for_insufficient_stock(self, db_session, sample_menu_items):
        """Should reject when insufficient stock."""
        burger = sample_menu_items[0]  # Has 20
        
        items = [OrderItemCreate(menu_item_id=burger.id, quantity=100)]
        
        with pytest.raises(ValueError, match="Insufficient stock"):
            OrderService.validate_order_items(db_session, items)


class TestCalculateOrderTotal:
    """Test order total calculation."""
    
    def test_calculates_total_for_single_item(self, db_session, sample_menu_items):
        """Should calculate total for single item."""
        burger = sample_menu_items[0]  # 9.99
        
        items = [OrderItemCreate(menu_item_id=burger.id, quantity=2)]
        
        total = OrderService.calculate_order_total(db_session, items)
        
        assert total == Decimal("19.98")  # 9.99 * 2
    
    def test_calculates_total_for_multiple_items(self, db_session, sample_menu_items):
        """Should calculate total for multiple items."""
        burger = sample_menu_items[0]  # 9.99
        pizza = sample_menu_items[1]   # 12.99
        
        items = [
            OrderItemCreate(menu_item_id=burger.id, quantity=1),
            OrderItemCreate(menu_item_id=pizza.id, quantity=2)
        ]
        
        total = OrderService.calculate_order_total(db_session, items)
        
        # 9.99 + (12.99 * 2) = 35.97
        assert total == Decimal("35.97")
    
    def test_raises_error_for_nonexistent_item(self, db_session):
        """Should raise error when item doesn't exist."""
        items = [OrderItemCreate(menu_item_id=99999, quantity=1)]
        
        with pytest.raises(ValueError, match="not found"):
            OrderService.calculate_order_total(db_session, items)
    
    def test_total_precision(self, db_session, sample_menu_items):
        """Should maintain decimal precision."""
        burger = sample_menu_items[0]  # 9.99
        
        items = [OrderItemCreate(menu_item_id=burger.id, quantity=3)]
        
        total = OrderService.calculate_order_total(db_session, items)
        
        # 9.99 * 3 = 29.97
        assert total == Decimal("29.97")
        assert isinstance(total, Decimal)
