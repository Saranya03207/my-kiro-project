"""
Unit tests for order Pydantic schemas.
Tests validation rules for OrderCreate, OrderItemCreate, OrderResponse, and OrderItemResponse.
"""
import pytest
from decimal import Decimal
from pydantic import ValidationError
from backend.schemas.order import (
    OrderCreate,
    OrderItemCreate,
    OrderResponse,
    OrderItemResponse
)
from datetime import datetime


class TestOrderItemCreate:
    """Tests for OrderItemCreate schema validation."""
    
    def test_valid_order_item_create(self):
        """Valid order item with menu_item_id and quantity passes validation."""
        data = {
            "menu_item_id": 1,
            "quantity": 2
        }
        item = OrderItemCreate(**data)
        assert item.menu_item_id == 1
        assert item.quantity == 2
    
    def test_quantity_one_valid(self):
        """Minimum quantity of 1 passes validation."""
        item = OrderItemCreate(menu_item_id=5, quantity=1)
        assert item.quantity == 1
    
    def test_large_quantity_valid(self):
        """Large quantity passes validation."""
        item = OrderItemCreate(menu_item_id=1, quantity=100)
        assert item.quantity == 100
    
    def test_quantity_zero_fails(self):
        """Quantity of 0 fails validation (minimum is 1)."""
        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(menu_item_id=1, quantity=0)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_quantity_negative_fails(self):
        """Negative quantity fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(menu_item_id=1, quantity=-1)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_menu_item_id_zero_fails(self):
        """menu_item_id of 0 fails validation (must be > 0)."""
        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(menu_item_id=0, quantity=1)
        assert "menu_item_id" in str(exc_info.value).lower()
    
    def test_menu_item_id_negative_fails(self):
        """Negative menu_item_id fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(menu_item_id=-1, quantity=1)
        assert "menu_item_id" in str(exc_info.value).lower()
    
    def test_missing_menu_item_id_fails(self):
        """Missing menu_item_id fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(quantity=1)
        assert "menu_item_id" in str(exc_info.value).lower()
    
    def test_missing_quantity_fails(self):
        """Missing quantity fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(menu_item_id=1)
        assert "quantity" in str(exc_info.value).lower()


class TestOrderCreate:
    """Tests for OrderCreate schema validation."""
    
    def test_valid_order_with_one_item(self):
        """Valid order with one item passes validation."""
        data = {
            "items": [
                {"menu_item_id": 1, "quantity": 2}
            ]
        }
        order = OrderCreate(**data)
        assert len(order.items) == 1
        assert order.items[0].menu_item_id == 1
        assert order.items[0].quantity == 2
    
    def test_valid_order_with_multiple_items(self):
        """Valid order with multiple items passes validation."""
        data = {
            "items": [
                {"menu_item_id": 1, "quantity": 2},
                {"menu_item_id": 2, "quantity": 1},
                {"menu_item_id": 3, "quantity": 5}
            ]
        }
        order = OrderCreate(**data)
        assert len(order.items) == 3
        assert order.items[0].menu_item_id == 1
        assert order.items[1].menu_item_id == 2
        assert order.items[2].menu_item_id == 3
    
    def test_empty_items_list_fails(self):
        """Order with empty items list fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            OrderCreate(items=[])
        assert "items" in str(exc_info.value).lower()
    
    def test_missing_items_fails(self):
        """Order without items field fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            OrderCreate()
        assert "items" in str(exc_info.value).lower()
    
    def test_invalid_item_in_list_fails(self):
        """Order with invalid item (quantity=0) fails validation."""
        with pytest.raises(ValidationError):
            OrderCreate(items=[
                {"menu_item_id": 1, "quantity": 0}
            ])
    
    def test_multiple_items_same_menu_item_valid(self):
        """Order with duplicate menu_item_id is valid (business logic handles this)."""
        data = {
            "items": [
                {"menu_item_id": 1, "quantity": 2},
                {"menu_item_id": 1, "quantity": 3}
            ]
        }
        order = OrderCreate(**data)
        assert len(order.items) == 2
    
    def test_nested_validation_applies(self):
        """Validation rules from OrderItemCreate apply to items in order."""
        # Test negative quantity in nested item
        with pytest.raises(ValidationError):
            OrderCreate(items=[
                {"menu_item_id": 1, "quantity": -1}
            ])
        
        # Test zero menu_item_id in nested item
        with pytest.raises(ValidationError):
            OrderCreate(items=[
                {"menu_item_id": 0, "quantity": 1}
            ])


class TestOrderItemResponse:
    """Tests for OrderItemResponse schema."""
    
    def test_valid_order_item_response(self):
        """Create valid OrderItemResponse from dictionary."""
        data = {
            "menu_item_id": 1,
            "quantity": 2,
            "price_at_order_time": Decimal("9.99")
        }
        item = OrderItemResponse(**data)
        assert item.menu_item_id == 1
        assert item.quantity == 2
        assert item.price_at_order_time == Decimal("9.99")
    
    def test_all_fields_required(self):
        """All required fields must be provided."""
        # Missing quantity
        with pytest.raises(ValidationError):
            OrderItemResponse(
                menu_item_id=1,
                price_at_order_time=Decimal("9.99")
            )
        
        # Missing menu_item_id
        with pytest.raises(ValidationError):
            OrderItemResponse(
                quantity=2,
                price_at_order_time=Decimal("9.99")
            )


class TestOrderResponse:
    """Tests for OrderResponse schema."""
    
    def test_valid_order_response_with_items(self):
        """Create valid OrderResponse with items from dictionary."""
        data = {
            "id": 123,
            "student_id": "S001",
            "total_price": Decimal("19.98"),
            "status": "pending",
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 2,
                    "price_at_order_time": Decimal("9.99")
                }
            ],
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 1, 12, 5, 0)
        }
        order = OrderResponse(**data)
        assert order.id == 123
        assert order.student_id == "S001"
        assert order.total_price == Decimal("19.98")
        assert order.status == "pending"
        assert len(order.items) == 1
        assert order.items[0].menu_item_id == 1
        assert order.items[0].quantity == 2
        assert order.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert order.updated_at == datetime(2024, 1, 1, 12, 5, 0)
    
    def test_valid_order_response_multiple_items(self):
        """OrderResponse with multiple items."""
        data = {
            "id": 456,
            "student_id": "S002",
            "total_price": Decimal("29.97"),
            "status": "preparing",
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 1,
                    "price_at_order_time": Decimal("9.99")
                },
                {
                    "menu_item_id": 2,
                    "quantity": 1,
                    "price_at_order_time": Decimal("12.99")
                },
                {
                    "menu_item_id": 3,
                    "quantity": 2,
                    "price_at_order_time": Decimal("3.49")
                }
            ],
            "created_at": datetime(2024, 1, 2, 10, 0, 0),
            "updated_at": datetime(2024, 1, 2, 10, 10, 0)
        }
        order = OrderResponse(**data)
        assert len(order.items) == 3
        assert order.total_price == Decimal("29.97")
    
    def test_updated_at_can_be_none(self):
        """OrderResponse with updated_at as None is valid."""
        data = {
            "id": 789,
            "student_id": "S003",
            "total_price": Decimal("5.99"),
            "status": "pending",
            "items": [
                {
                    "menu_item_id": 1,
                    "quantity": 1,
                    "price_at_order_time": Decimal("5.99")
                }
            ],
            "created_at": datetime(2024, 1, 3, 14, 0, 0),
            "updated_at": None
        }
        order = OrderResponse(**data)
        assert order.updated_at is None
    
    def test_empty_items_list_valid(self):
        """OrderResponse with empty items list is technically valid for the schema."""
        data = {
            "id": 100,
            "student_id": "S004",
            "total_price": Decimal("0.00"),
            "status": "cancelled",
            "items": [],
            "created_at": datetime(2024, 1, 4, 9, 0, 0),
            "updated_at": datetime(2024, 1, 4, 9, 1, 0)
        }
        order = OrderResponse(**data)
        assert len(order.items) == 0
    
    def test_all_required_fields_except_updated_at(self):
        """All fields except updated_at are required."""
        # Missing status
        with pytest.raises(ValidationError):
            OrderResponse(
                id=1,
                student_id="S001",
                total_price=Decimal("10.00"),
                items=[],
                created_at=datetime.now()
            )
        
        # Missing items
        with pytest.raises(ValidationError):
            OrderResponse(
                id=1,
                student_id="S001",
                total_price=Decimal("10.00"),
                status="pending",
                created_at=datetime.now()
            )
    
    def test_status_variations(self):
        """Different status values are valid strings."""
        statuses = ["pending", "preparing", "ready", "completed", "cancelled"]
        for status in statuses:
            data = {
                "id": 1,
                "student_id": "S001",
                "total_price": Decimal("10.00"),
                "status": status,
                "items": [],
                "created_at": datetime.now()
            }
            order = OrderResponse(**data)
            assert order.status == status
