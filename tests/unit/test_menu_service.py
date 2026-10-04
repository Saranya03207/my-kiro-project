"""
Unit tests for menu service.
Tests menu item retrieval, creation, updates, and management.
"""
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models.menu_item import MenuItem
from backend.schemas.menu_item import MenuItemCreate, MenuItemUpdate
from backend.services.menu_service import MenuService


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
    """Create sample menu items for testing."""
    items = [
        MenuItem(
            name="Burger",
            description="Beef burger with lettuce",
            price=Decimal("9.99"),
            category="Meals",
            stock_quantity=10,
            stock_threshold=5,
            is_available=True,
            is_deleted=False
        ),
        MenuItem(
            name="Pizza",
            description="Cheese pizza",
            price=Decimal("12.99"),
            category="Meals",
            stock_quantity=5,
            stock_threshold=3,
            is_available=True,
            is_deleted=False
        ),
        MenuItem(
            name="Soda",
            description="Carbonated soft drink",
            price=Decimal("2.99"),
            category="Beverages",
            stock_quantity=20,
            stock_threshold=10,
            is_available=True,
            is_deleted=False
        ),
        MenuItem(
            name="Fries",
            description="Crispy french fries",
            price=Decimal("3.99"),
            category="Snacks",
            stock_quantity=15,
            stock_threshold=5,
            is_available=False,  # Unavailable
            is_deleted=False
        ),
        MenuItem(
            name="Old Burger",
            description="Old menu item",
            price=Decimal("8.99"),
            category="Meals",
            stock_quantity=0,
            stock_threshold=5,
            is_available=False,
            is_deleted=True  # Soft deleted
        )
    ]
    for item in items:
        db_session.add(item)
    db_session.commit()
    return items


class TestGetAvailableMenuItems:
    """Test getting available menu items."""
    
    def test_returns_only_available_items(self, db_session, sample_menu_items):
        """Should return only available items by default."""
        items = MenuService.get_available_menu_items(db_session)
        
        # Should return 3 items (Burger, Pizza, Soda) - not Fries (unavailable) or Old Burger (deleted)
        assert len(items) == 3
        names = [item.name for item in items]
        assert "Burger" in names
        assert "Pizza" in names
        assert "Soda" in names
        assert "Fries" not in names
        assert "Old Burger" not in names
    
    def test_includes_unavailable_when_requested(self, db_session, sample_menu_items):
        """Should include unavailable items when include_unavailable=True."""
        items = MenuService.get_available_menu_items(db_session, include_unavailable=True)
        
        # Should return 4 items (including Fries) but not Old Burger (deleted)
        assert len(items) == 4
        names = [item.name for item in items]
        assert "Fries" in names
        assert "Old Burger" not in names
    
    def test_sorts_by_category_then_name(self, db_session, sample_menu_items):
        """Should sort items by category, then by name."""
        items = MenuService.get_available_menu_items(db_session)
        
        # Expected order: Beverages (Soda), Meals (Burger, Pizza)
        assert items[0].category == "Beverages"
        assert items[0].name == "Soda"
        assert items[1].category == "Meals"
        assert items[1].name == "Burger"
        assert items[2].category == "Meals"
        assert items[2].name == "Pizza"
    
    def test_returns_empty_list_when_no_items(self, db_session):
        """Should return empty list when no items exist."""
        items = MenuService.get_available_menu_items(db_session)
        assert items == []


class TestGetMenuItemById:
    """Test getting menu item by ID."""
    
    def test_returns_item_when_found(self, db_session, sample_menu_items):
        """Should return menu item when ID exists."""
        burger = sample_menu_items[0]
        
        item = MenuService.get_menu_item_by_id(db_session, burger.id)
        
        assert item is not None
        assert item.id == burger.id
        assert item.name == "Burger"
    
    def test_returns_none_when_not_found(self, db_session, sample_menu_items):
        """Should return None when ID doesn't exist."""
        item = MenuService.get_menu_item_by_id(db_session, 99999)
        assert item is None
    
    def test_returns_none_for_deleted_item(self, db_session, sample_menu_items):
        """Should return None for soft-deleted items."""
        old_burger = sample_menu_items[4]
        
        item = MenuService.get_menu_item_by_id(db_session, old_burger.id)
        
        assert item is None


class TestSearchMenuItems:
    """Test searching and filtering menu items."""
    
    def test_search_by_name(self, db_session, sample_menu_items):
        """Should find items matching name."""
        items = MenuService.search_menu_items(db_session, search="burger")
        
        assert len(items) == 1
        assert items[0].name == "Burger"
    
    def test_search_by_description(self, db_session, sample_menu_items):
        """Should find items matching description."""
        items = MenuService.search_menu_items(db_session, search="pizza")
        
        assert len(items) == 1
        assert items[0].name == "Pizza"
    
    def test_search_case_insensitive(self, db_session, sample_menu_items):
        """Should perform case-insensitive search."""
        items = MenuService.search_menu_items(db_session, search="BURGER")
        assert len(items) == 1
        
        items = MenuService.search_menu_items(db_session, search="burger")
        assert len(items) == 1
        
        items = MenuService.search_menu_items(db_session, search="BuRgEr")
        assert len(items) == 1
    
    def test_filter_by_category(self, db_session, sample_menu_items):
        """Should filter items by category."""
        items = MenuService.search_menu_items(db_session, category="Meals")
        
        assert len(items) == 2
        assert all(item.category == "Meals" for item in items)
    
    def test_search_and_category_combined(self, db_session, sample_menu_items):
        """Should apply both search and category filters."""
        items = MenuService.search_menu_items(
            db_session,
            search="burger",
            category="Meals"
        )
        
        assert len(items) == 1
        assert items[0].name == "Burger"
    
    def test_excludes_unavailable_by_default(self, db_session, sample_menu_items):
        """Should exclude unavailable items by default."""
        items = MenuService.search_menu_items(db_session, category="Snacks")
        
        # Fries is in Snacks but unavailable
        assert len(items) == 0
    
    def test_includes_unavailable_when_requested(self, db_session, sample_menu_items):
        """Should include unavailable items when requested."""
        items = MenuService.search_menu_items(
            db_session,
            category="Snacks",
            include_unavailable=True
        )
        
        assert len(items) == 1
        assert items[0].name == "Fries"
    
    def test_excludes_deleted_items(self, db_session, sample_menu_items):
        """Should never return deleted items."""
        items = MenuService.search_menu_items(
            db_session,
            search="Old",
            include_unavailable=True
        )
        
        assert len(items) == 0


class TestCreateMenuItem:
    """Test creating menu items."""
    
    def test_creates_item_successfully(self, db_session):
        """Should create a new menu item."""
        item_data = MenuItemCreate(
            name="Salad",
            description="Fresh garden salad",
            price=Decimal("6.99"),
            category="Meals",
            stock_quantity=10,
            stock_threshold=5
        )
        
        item = MenuService.create_menu_item(db_session, item_data)
        
        assert item.id is not None
        assert item.name == "Salad"
        assert item.description == "Fresh garden salad"
        assert item.price == Decimal("6.99")
        assert item.category == "Meals"
        assert item.stock_quantity == 10
        assert item.stock_threshold == 5
        assert item.is_available is True
        assert item.is_deleted is False
    
    def test_raises_error_for_duplicate_name(self, db_session, sample_menu_items):
        """Should raise ValueError when name already exists."""
        item_data = MenuItemCreate(
            name="Burger",  # Already exists
            description="Another burger",
            price=Decimal("10.99"),
            category="Meals",
            stock_quantity=5,
            stock_threshold=2
        )
        
        with pytest.raises(ValueError, match="already exists"):
            MenuService.create_menu_item(db_session, item_data)
    
    def test_cannot_create_duplicate_of_deleted_item(self, db_session, sample_menu_items):
        """Should not allow creating item with same name as deleted item due to DB constraint."""
        # Old Burger is deleted, but database UNIQUE constraint on name still prevents duplicates
        item_data = MenuItemCreate(
            name="Old Burger",  # Deleted item name
            description="New burger replacing old one",
            price=Decimal("11.99"),
            category="Meals",
            stock_quantity=15,
            stock_threshold=5
        )
        
        # Should raise error due to database UNIQUE constraint
        with pytest.raises(ValueError, match="Failed to create menu item"):
            MenuService.create_menu_item(db_session, item_data)


class TestUpdateMenuItem:
    """Test updating menu items."""
    
    def test_updates_single_field(self, db_session, sample_menu_items):
        """Should update a single field without affecting others."""
        burger = sample_menu_items[0]
        original_description = burger.description
        original_price = burger.price
        
        update_data = MenuItemUpdate(name="Super Burger")
        
        updated = MenuService.update_menu_item(db_session, burger.id, update_data)
        
        assert updated is not None
        assert updated.name == "Super Burger"
        assert updated.description == original_description
        assert updated.price == original_price
    
    def test_updates_multiple_fields(self, db_session, sample_menu_items):
        """Should update multiple fields."""
        burger = sample_menu_items[0]
        
        update_data = MenuItemUpdate(
            name="Premium Burger",
            price=Decimal("12.99"),
            description="Premium beef burger"
        )
        
        updated = MenuService.update_menu_item(db_session, burger.id, update_data)
        
        assert updated.name == "Premium Burger"
        assert updated.price == Decimal("12.99")
        assert updated.description == "Premium beef burger"
    
    def test_partial_update_preserves_unset_fields(self, db_session, sample_menu_items):
        """Should preserve fields not included in update."""
        burger = sample_menu_items[0]
        original_stock = burger.stock_quantity
        original_category = burger.category
        
        update_data = MenuItemUpdate(price=Decimal("11.99"))
        
        updated = MenuService.update_menu_item(db_session, burger.id, update_data)
        
        assert updated.price == Decimal("11.99")
        assert updated.stock_quantity == original_stock
        assert updated.category == original_category
    
    def test_returns_none_for_nonexistent_item(self, db_session):
        """Should return None when item doesn't exist."""
        update_data = MenuItemUpdate(name="New Name")
        
        updated = MenuService.update_menu_item(db_session, 99999, update_data)
        
        assert updated is None
    
    def test_raises_error_for_duplicate_name(self, db_session, sample_menu_items):
        """Should raise ValueError when updating to existing name."""
        burger = sample_menu_items[0]
        
        update_data = MenuItemUpdate(name="Pizza")  # Already exists
        
        with pytest.raises(ValueError, match="already exists"):
            MenuService.update_menu_item(db_session, burger.id, update_data)
    
    def test_allows_keeping_same_name(self, db_session, sample_menu_items):
        """Should allow updating other fields without changing name."""
        burger = sample_menu_items[0]
        
        update_data = MenuItemUpdate(
            name="Burger",  # Same name
            price=Decimal("10.99")
        )
        
        updated = MenuService.update_menu_item(db_session, burger.id, update_data)
        
        assert updated is not None
        assert updated.name == "Burger"
        assert updated.price == Decimal("10.99")
    
    def test_cannot_update_deleted_item(self, db_session, sample_menu_items):
        """Should return None when trying to update deleted item."""
        old_burger = sample_menu_items[4]
        
        update_data = MenuItemUpdate(name="Revived Burger")
        
        updated = MenuService.update_menu_item(db_session, old_burger.id, update_data)
        
        assert updated is None


class TestToggleAvailability:
    """Test toggling item availability."""
    
    def test_toggles_available_to_unavailable(self, db_session, sample_menu_items):
        """Should toggle available item to unavailable."""
        burger = sample_menu_items[0]
        assert burger.is_available is True
        
        updated = MenuService.toggle_availability(db_session, burger.id)
        
        assert updated is not None
        assert updated.is_available is False
    
    def test_toggles_unavailable_to_available(self, db_session, sample_menu_items):
        """Should toggle unavailable item to available."""
        fries = sample_menu_items[3]
        assert fries.is_available is False
        
        updated = MenuService.toggle_availability(db_session, fries.id)
        
        assert updated is not None
        assert updated.is_available is True
    
    def test_toggle_is_reversible(self, db_session, sample_menu_items):
        """Should toggle back and forth correctly."""
        burger = sample_menu_items[0]
        original_status = burger.is_available
        
        # Toggle once
        MenuService.toggle_availability(db_session, burger.id)
        db_session.refresh(burger)
        assert burger.is_available is not original_status
        
        # Toggle back
        MenuService.toggle_availability(db_session, burger.id)
        db_session.refresh(burger)
        assert burger.is_available is original_status
    
    def test_returns_none_for_nonexistent_item(self, db_session):
        """Should return None when item doesn't exist."""
        updated = MenuService.toggle_availability(db_session, 99999)
        assert updated is None
    
    def test_cannot_toggle_deleted_item(self, db_session, sample_menu_items):
        """Should return None when trying to toggle deleted item."""
        old_burger = sample_menu_items[4]
        
        updated = MenuService.toggle_availability(db_session, old_burger.id)
        
        assert updated is None


class TestDeleteMenuItem:
    """Test soft deleting menu items."""
    
    def test_soft_deletes_item(self, db_session, sample_menu_items):
        """Should mark item as deleted without removing from database."""
        burger = sample_menu_items[0]
        burger_id = burger.id
        
        result = MenuService.delete_menu_item(db_session, burger_id)
        
        assert result is True
        
        # Item still exists in database
        db_session.refresh(burger)
        assert burger.is_deleted is True
        assert burger.is_available is False
        
        # But not returned by normal queries
        item = MenuService.get_menu_item_by_id(db_session, burger_id)
        assert item is None
    
    def test_marks_as_unavailable_on_delete(self, db_session, sample_menu_items):
        """Should mark item as unavailable when deleted."""
        burger = sample_menu_items[0]
        assert burger.is_available is True
        
        MenuService.delete_menu_item(db_session, burger.id)
        
        db_session.refresh(burger)
        assert burger.is_available is False
    
    def test_returns_false_for_nonexistent_item(self, db_session):
        """Should return False when item doesn't exist."""
        result = MenuService.delete_menu_item(db_session, 99999)
        assert result is False
    
    def test_returns_false_for_already_deleted_item(self, db_session, sample_menu_items):
        """Should return False when trying to delete already deleted item."""
        old_burger = sample_menu_items[4]
        
        result = MenuService.delete_menu_item(db_session, old_burger.id)
        
        assert result is False
    
    def test_deleted_item_not_in_available_list(self, db_session, sample_menu_items):
        """Should exclude deleted items from get_available_menu_items."""
        burger = sample_menu_items[0]
        
        # Before delete
        items = MenuService.get_available_menu_items(db_session)
        assert len(items) == 3
        
        # Delete
        MenuService.delete_menu_item(db_session, burger.id)
        
        # After delete
        items = MenuService.get_available_menu_items(db_session)
        assert len(items) == 2
        assert all(item.name != "Burger" for item in items)
    
    def test_preserves_historical_data(self, db_session, sample_menu_items):
        """Should preserve item data after deletion for historical references."""
        burger = sample_menu_items[0]
        original_name = burger.name
        original_price = burger.price
        
        MenuService.delete_menu_item(db_session, burger.id)
        
        # Item data is preserved in database
        db_session.refresh(burger)
        assert burger.name == original_name
        assert burger.price == original_price
