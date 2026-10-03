"""
Unit tests for menu item Pydantic schemas.
Tests validation rules for MenuItemCreate, MenuItemUpdate, and MenuItemResponse.
"""
import pytest
from decimal import Decimal
from pydantic import ValidationError
from backend.schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemResponse
from datetime import datetime


class TestMenuItemCreate:
    """Tests for MenuItemCreate schema validation."""
    
    def test_valid_menu_item_create(self):
        """Valid menu item with all required fields passes validation."""
        data = {
            "name": "Burger",
            "description": "Delicious beef burger",
            "price": Decimal("9.99"),
            "category": "Meals",
            "stock_quantity": 10
        }
        item = MenuItemCreate(**data)
        assert item.name == "Burger"
        assert item.description == "Delicious beef burger"
        assert item.price == Decimal("9.99")
        assert item.category == "Meals"
        assert item.stock_quantity == 10
        assert item.stock_threshold == 5  # Default value
    
    def test_custom_stock_threshold(self):
        """Menu item with custom stock threshold."""
        data = {
            "name": "Pizza",
            "description": "Cheese pizza",
            "price": Decimal("12.99"),
            "category": "Meals",
            "stock_quantity": 5,
            "stock_threshold": 3
        }
        item = MenuItemCreate(**data)
        assert item.stock_threshold == 3
    
    def test_name_too_long_fails(self):
        """Name exceeding 100 characters fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MenuItemCreate(
                name="A" * 101,
                description="Test",
                price=Decimal("9.99"),
                category="Meals",
                stock_quantity=10
            )
        assert "name" in str(exc_info.value)
    
    def test_name_empty_fails(self):
        """Empty name fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MenuItemCreate(
                name="",
                description="Test",
                price=Decimal("9.99"),
                category="Meals",
                stock_quantity=10
            )
        assert "name" in str(exc_info.value)
    
    def test_name_whitespace_only_fails(self):
        """Name with only whitespace fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MenuItemCreate(
                name="   ",
                description="Test",
                price=Decimal("9.99"),
                category="Meals",
                stock_quantity=10
            )
        assert "whitespace" in str(exc_info.value).lower()
    
    def test_description_too_long_fails(self):
        """Description exceeding 500 characters fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MenuItemCreate(
                name="Burger",
                description="A" * 501,
                price=Decimal("9.99"),
                category="Meals",
                stock_quantity=10
            )
        assert "description" in str(exc_info.value)
    
    def test_description_empty_fails(self):
        """Empty description fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MenuItemCreate(
                name="Burger",
                description="",
                price=Decimal("9.99"),
                category="Meals",
                stock_quantity=10
            )
        assert "description" in str(exc_info.value)
    
    def test_price_zero_fails(self):
        """Price of 0 fails validation (minimum is 0.01)."""
        with pytest.raises(ValidationError) as exc_info:
            MenuItemCreate(
                name="Burger",
                description="Test",
                price=Decimal("0.00"),
                category="Meals",
                stock_quantity=10
            )
        assert "price" in str(exc_info.value)
    
    def test_price_negative_fails(self):
        """Negative price fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MenuItemCreate(
                name="Burger",
                description="Test",
                price=Decimal("-5.00"),
                category="Meals",
                stock_quantity=10
            )
        assert "price" in str(exc_info.value)
    
    def test_price_too_many_decimals_fails(self):
        """Price with more than 2 decimal places fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MenuItemCreate(
                name="Burger",
                description="Test",
                price=Decimal("9.999"),
                category="Meals",
                stock_quantity=10
            )
        assert "decimal" in str(exc_info.value).lower()
    
    def test_price_minimum_valid(self):
        """Price of 0.01 (minimum) passes validation."""
        item = MenuItemCreate(
            name="Cheap Item",
            description="Very cheap",
            price=Decimal("0.01"),
            category="Snacks",
            stock_quantity=100
        )
        assert item.price == Decimal("0.01")
    
    def test_price_large_valid(self):
        """Large valid price passes validation."""
        item = MenuItemCreate(
            name="Expensive Item",
            description="Very expensive",
            price=Decimal("9999.99"),
            category="Meals",
            stock_quantity=1
        )
        assert item.price == Decimal("9999.99")
    
    def test_category_empty_fails(self):
        """Empty category fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MenuItemCreate(
                name="Burger",
                description="Test",
                price=Decimal("9.99"),
                category="",
                stock_quantity=10
            )
        assert "category" in str(exc_info.value)
    
    def test_category_too_long_fails(self):
        """Category exceeding 50 characters fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MenuItemCreate(
                name="Burger",
                description="Test",
                price=Decimal("9.99"),
                category="A" * 51,
                stock_quantity=10
            )
        assert "category" in str(exc_info.value)
    
    def test_stock_quantity_negative_fails(self):
        """Negative stock quantity fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MenuItemCreate(
                name="Burger",
                description="Test",
                price=Decimal("9.99"),
                category="Meals",
                stock_quantity=-1
            )
        assert "stock_quantity" in str(exc_info.value)
    
    def test_stock_quantity_zero_valid(self):
        """Stock quantity of 0 passes validation."""
        item = MenuItemCreate(
            name="Out of Stock",
            description="Currently unavailable",
            price=Decimal("5.99"),
            category="Snacks",
            stock_quantity=0
        )
        assert item.stock_quantity == 0
    
    def test_stock_threshold_negative_fails(self):
        """Negative stock threshold fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MenuItemCreate(
                name="Burger",
                description="Test",
                price=Decimal("9.99"),
                category="Meals",
                stock_quantity=10,
                stock_threshold=-1
            )
        assert "stock_threshold" in str(exc_info.value)
    
    def test_whitespace_trimmed(self):
        """Whitespace in name and category is trimmed."""
        item = MenuItemCreate(
            name="  Burger  ",
            description="  Test description  ",
            price=Decimal("9.99"),
            category="  Meals  ",
            stock_quantity=10
        )
        assert item.name == "Burger"
        assert item.description == "Test description"
        assert item.category == "Meals"


class TestMenuItemUpdate:
    """Tests for MenuItemUpdate schema validation."""
    
    def test_all_fields_none_valid(self):
        """Update with all fields as None is valid (no changes)."""
        update = MenuItemUpdate()
        assert update.name is None
        assert update.description is None
        assert update.price is None
        assert update.category is None
        assert update.stock_quantity is None
        assert update.stock_threshold is None
        assert update.is_available is None
    
    def test_partial_update_name_only(self):
        """Update with only name field."""
        update = MenuItemUpdate(name="New Name")
        assert update.name == "New Name"
        assert update.price is None
    
    def test_partial_update_price_only(self):
        """Update with only price field."""
        update = MenuItemUpdate(price=Decimal("15.99"))
        assert update.price == Decimal("15.99")
        assert update.name is None
    
    def test_partial_update_multiple_fields(self):
        """Update with multiple fields."""
        update = MenuItemUpdate(
            name="Updated Burger",
            price=Decimal("11.99"),
            stock_quantity=20
        )
        assert update.name == "Updated Burger"
        assert update.price == Decimal("11.99")
        assert update.stock_quantity == 20
        assert update.category is None
    
    def test_update_is_available(self):
        """Update availability status."""
        update = MenuItemUpdate(is_available=False)
        assert update.is_available is False
    
    def test_name_validation_applies(self):
        """Name validation rules apply to updates."""
        with pytest.raises(ValidationError):
            MenuItemUpdate(name="A" * 101)
        
        with pytest.raises(ValidationError):
            MenuItemUpdate(name="")
        
        with pytest.raises(ValidationError):
            MenuItemUpdate(name="   ")
    
    def test_price_validation_applies(self):
        """Price validation rules apply to updates."""
        with pytest.raises(ValidationError):
            MenuItemUpdate(price=Decimal("0.00"))
        
        with pytest.raises(ValidationError):
            MenuItemUpdate(price=Decimal("-5.00"))
        
        with pytest.raises(ValidationError):
            MenuItemUpdate(price=Decimal("9.999"))
    
    def test_stock_validation_applies(self):
        """Stock validation rules apply to updates."""
        with pytest.raises(ValidationError):
            MenuItemUpdate(stock_quantity=-1)
        
        with pytest.raises(ValidationError):
            MenuItemUpdate(stock_threshold=-1)
    
    def test_whitespace_trimmed_in_update(self):
        """Whitespace is trimmed in update fields."""
        update = MenuItemUpdate(
            name="  Updated  ",
            category="  New Category  "
        )
        assert update.name == "Updated"
        assert update.category == "New Category"


class TestMenuItemResponse:
    """Tests for MenuItemResponse schema."""
    
    def test_response_from_dict(self):
        """Create response from dictionary."""
        data = {
            "id": 1,
            "name": "Burger",
            "description": "Beef burger",
            "price": Decimal("9.99"),
            "category": "Meals",
            "stock_quantity": 10,
            "is_available": True,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 2, 12, 0, 0)
        }
        response = MenuItemResponse(**data)
        assert response.id == 1
        assert response.name == "Burger"
        assert response.price == Decimal("9.99")
        assert response.is_available is True
        assert response.created_at == datetime(2024, 1, 1, 12, 0, 0)
        assert response.updated_at == datetime(2024, 1, 2, 12, 0, 0)
    
    def test_response_updated_at_none(self):
        """Response with updated_at as None is valid."""
        data = {
            "id": 1,
            "name": "Burger",
            "description": "Beef burger",
            "price": Decimal("9.99"),
            "category": "Meals",
            "stock_quantity": 10,
            "is_available": True,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": None
        }
        response = MenuItemResponse(**data)
        assert response.updated_at is None
    
    def test_response_all_required_fields(self):
        """Response requires all fields except updated_at."""
        with pytest.raises(ValidationError):
            MenuItemResponse(
                name="Burger",
                description="Test",
                price=Decimal("9.99")
                # Missing id, category, stock_quantity, is_available, created_at
            )
