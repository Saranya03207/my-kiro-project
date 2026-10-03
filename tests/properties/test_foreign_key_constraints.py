"""
Property-based tests for foreign key constraint enforcement.
Tests that database properly enforces referential integrity between tables.
"""
import pytest
from hypothesis import given, strategies as st, settings
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

from backend.database import Base
from backend.models.menu_item import MenuItem
from backend.models.order import Order
from backend.models.order_item import OrderItem


def create_test_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        # Enable foreign key constraint enforcement in SQLite
        connect_args={"check_same_thread": False},
        poolclass=None
    )
    
    # CRITICAL: Enable foreign key constraints in SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


# Feature: smart-canteen-manager, Property 54: Foreign Key Constraint Enforcement (Orders to OrderItems)
@given(
    order_id=st.integers(min_value=1000, max_value=9999),
    menu_item_id=st.integers(min_value=1, max_value=100),
    quantity=st.integers(min_value=1, max_value=10),
    price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999.99"), places=2)
)
@settings(max_examples=100)
def test_order_item_requires_valid_order_id(order_id, menu_item_id, quantity, price):
    """
    Property: Cannot create OrderItem with non-existent order_id.
    Validates: Requirements 18.5
    
    For any attempt to create an order_item with order_id O,
    the operation SHALL fail if no order with id O exists in the orders table.
    """
    test_db = create_test_db()
    
    try:
        # Ensure the order_id doesn't exist by checking and using a non-existent one
        existing_order = test_db.query(Order).filter(Order.id == order_id).first()
        if existing_order:
            test_db.close()
            pytest.skip("Generated order_id already exists")
        
        # Create a menu item (required for foreign key)
        menu_item = MenuItem(
            id=menu_item_id,
            name=f"Test Item {menu_item_id}",
            description="Test description",
            price=price,
            category="Test",
            stock_quantity=10,
            stock_threshold=5
        )
        test_db.add(menu_item)
        test_db.commit()
        
        # Attempt to create OrderItem with non-existent order_id
        order_item = OrderItem(
            order_id=order_id,  # Non-existent order
            menu_item_id=menu_item_id,
            quantity=quantity,
            price_at_order_time=price
        )
        test_db.add(order_item)
        
        # This should fail with IntegrityError due to foreign key constraint
        with pytest.raises(IntegrityError):
            test_db.commit()
        
        test_db.rollback()
    finally:
        test_db.close()


# Feature: smart-canteen-manager, Property 55: Foreign Key Constraint Enforcement (OrderItems to MenuItems)
@given(
    student_id=st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
    menu_item_id=st.integers(min_value=1000, max_value=9999),
    quantity=st.integers(min_value=1, max_value=10),
    price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999.99"), places=2)
)
@settings(max_examples=100)
def test_order_item_requires_valid_menu_item_id(student_id, menu_item_id, quantity, price):
    """
    Property: Cannot create OrderItem with non-existent menu_item_id.
    Validates: Requirements 18.6
    
    For any attempt to create an order_item with menu_item_id M,
    the operation SHALL fail if no menu_item with id M exists in the menu_items table.
    """
    test_db = create_test_db()
    
    try:
        # Ensure the menu_item_id doesn't exist
        existing_menu_item = test_db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
        if existing_menu_item:
            test_db.close()
            pytest.skip("Generated menu_item_id already exists")
        
        # Create an order (required for foreign key)
        order = Order(
            student_id=student_id,
            total_price=price,
            status="pending"
        )
        test_db.add(order)
        test_db.commit()
        
        # Attempt to create OrderItem with non-existent menu_item_id
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item_id,  # Non-existent menu item
            quantity=quantity,
            price_at_order_time=price
        )
        test_db.add(order_item)
        
        # This should fail with IntegrityError due to foreign key constraint
        with pytest.raises(IntegrityError):
            test_db.commit()
        
        test_db.rollback()
    finally:
        test_db.close()


# Additional test: Verify that valid foreign keys DO work
@given(
    student_id=st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))),
    quantity=st.integers(min_value=1, max_value=10),
    price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("999.99"), places=2)
)
@settings(max_examples=100)
def test_order_item_with_valid_foreign_keys_succeeds(student_id, quantity, price):
    """
    Property: OrderItem creation succeeds with valid foreign keys.
    
    This test verifies that when both order_id and menu_item_id reference
    existing records, the OrderItem can be created successfully.
    """
    test_db = create_test_db()
    
    try:
        # Create a menu item
        menu_item = MenuItem(
            name=f"Valid Item {student_id}",
            description="Test description",
            price=price,
            category="Test",
            stock_quantity=10,
            stock_threshold=5
        )
        test_db.add(menu_item)
        test_db.commit()
        
        # Create an order
        order = Order(
            student_id=student_id,
            total_price=price * quantity,
            status="pending"
        )
        test_db.add(order)
        test_db.commit()
        
        # Create OrderItem with valid foreign keys
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            quantity=quantity,
            price_at_order_time=price
        )
        test_db.add(order_item)
        test_db.commit()
        
        # Verify the order_item was created
        assert order_item.id is not None
        assert order_item.order_id == order.id
        assert order_item.menu_item_id == menu_item.id
        assert order_item.quantity == quantity
        
        # Verify relationships work
        assert order_item.order == order
        assert order_item.menu_item == menu_item
    finally:
        test_db.close()
