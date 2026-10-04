"""
Unit tests for inventory service.
Tests stock management, inventory tracking, and low-stock alerts.
"""
import pytest
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models.menu_item import MenuItem
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
    """Create sample menu items with various stock levels."""
    items = [
        MenuItem(
            name="Burger",
            description="Beef burger",
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
            stock_quantity=2,  # Below threshold
            stock_threshold=5,
            is_available=True,
            is_deleted=False
        ),
        MenuItem(
            name="Soda",
            description="Soft drink",
            price=Decimal("2.99"),
            category="Beverages",
            stock_quantity=5,  # At threshold
            stock_threshold=5,
            is_available=True,
            is_deleted=False
        ),
        MenuItem(
            name="Fries",
            description="French fries",
            price=Decimal("3.99"),
            category="Snacks",
            stock_quantity=0,  # Out of stock
            stock_threshold=5,
            is_available=True,
            is_deleted=False
        ),
        MenuItem(
            name="Old Item",
            description="Deleted item",
            price=Decimal("5.99"),
            category="Meals",
            stock_quantity=1,  # Below threshold
            stock_threshold=5,
            is_available=False,
            is_deleted=True  # Deleted
        )
    ]
    for item in items:
        db_session.add(item)
    db_session.commit()
    return items


class TestGetInventory:
    """Test retrieving inventory."""
    
    def test_returns_all_items(self, db_session, sample_menu_items):
        """Should return all menu items."""
        inventory = InventoryService.get_inventory(db_session)
        
        assert len(inventory) == 5
        names = [item.name for item in inventory]
        assert "Burger" in names
        assert "Pizza" in names
        assert "Soda" in names
        assert "Fries" in names
        assert "Old Item" in names
    
    def test_returns_empty_when_no_items(self, db_session):
        """Should return empty list when no items exist."""
        inventory = InventoryService.get_inventory(db_session)
        assert inventory == []
    
    def test_includes_stock_quantities(self, db_session, sample_menu_items):
        """Should include all stock quantities."""
        inventory = InventoryService.get_inventory(db_session)
        
        burger = next(item for item in inventory if item.name == "Burger")
        assert burger.stock_quantity == 10
        
        pizza = next(item for item in inventory if item.name == "Pizza")
        assert pizza.stock_quantity == 2


class TestUpdateStock:
    """Test updating stock quantity."""
    
    def test_sets_stock_to_specific_value(self, db_session, sample_menu_items):
        """Should set stock to exact value."""
        burger = sample_menu_items[0]
        
        updated = InventoryService.update_stock(db_session, burger.id, 25)
        
        assert updated is not None
        assert updated.stock_quantity == 25
    
    def test_can_set_stock_to_zero(self, db_session, sample_menu_items):
        """Should allow setting stock to 0."""
        burger = sample_menu_items[0]
        
        updated = InventoryService.update_stock(db_session, burger.id, 0)
        
        assert updated is not None
        assert updated.stock_quantity == 0
    
    def test_raises_error_for_negative_quantity(self, db_session, sample_menu_items):
        """Should reject negative stock quantities."""
        burger = sample_menu_items[0]
        
        with pytest.raises(ValueError, match="cannot be negative"):
            InventoryService.update_stock(db_session, burger.id, -5)
    
    def test_returns_none_for_nonexistent_item(self, db_session):
        """Should return None when item doesn't exist."""
        updated = InventoryService.update_stock(db_session, 99999, 10)
        assert updated is None
    
    def test_updates_deleted_item(self, db_session, sample_menu_items):
        """Should be able to update stock for deleted items."""
        old_item = sample_menu_items[4]
        
        updated = InventoryService.update_stock(db_session, old_item.id, 50)
        
        assert updated is not None
        assert updated.stock_quantity == 50


class TestIncrementStock:
    """Test incrementing stock quantity."""
    
    def test_adds_amount_to_stock(self, db_session, sample_menu_items):
        """Should add specified amount to current stock."""
        burger = sample_menu_items[0]
        original = burger.stock_quantity
        
        updated = InventoryService.increment_stock(db_session, burger.id, 5)
        
        assert updated is not None
        assert updated.stock_quantity == original + 5
    
    def test_increment_from_zero(self, db_session, sample_menu_items):
        """Should increment from zero stock."""
        fries = sample_menu_items[3]
        assert fries.stock_quantity == 0
        
        updated = InventoryService.increment_stock(db_session, fries.id, 10)
        
        assert updated.stock_quantity == 10
    
    def test_raises_error_for_zero_increment(self, db_session, sample_menu_items):
        """Should reject zero increment amount."""
        burger = sample_menu_items[0]
        
        with pytest.raises(ValueError, match="must be positive"):
            InventoryService.increment_stock(db_session, burger.id, 0)
    
    def test_raises_error_for_negative_increment(self, db_session, sample_menu_items):
        """Should reject negative increment amount."""
        burger = sample_menu_items[0]
        
        with pytest.raises(ValueError, match="must be positive"):
            InventoryService.increment_stock(db_session, burger.id, -5)
    
    def test_returns_none_for_nonexistent_item(self, db_session):
        """Should return None when item doesn't exist."""
        updated = InventoryService.increment_stock(db_session, 99999, 5)
        assert updated is None
    
    def test_multiple_increments_accumulate(self, db_session, sample_menu_items):
        """Should accumulate multiple increments."""
        burger = sample_menu_items[0]
        initial = burger.stock_quantity
        
        InventoryService.increment_stock(db_session, burger.id, 5)
        db_session.refresh(burger)
        InventoryService.increment_stock(db_session, burger.id, 3)
        db_session.refresh(burger)
        InventoryService.increment_stock(db_session, burger.id, 2)
        db_session.refresh(burger)
        
        assert burger.stock_quantity == initial + 10


class TestDecrementStock:
    """Test decrementing stock quantity."""
    
    def test_subtracts_amount_from_stock(self, db_session, sample_menu_items):
        """Should subtract specified amount from current stock."""
        burger = sample_menu_items[0]
        original = burger.stock_quantity
        
        updated = InventoryService.decrement_stock(db_session, burger.id, 3)
        
        assert updated is not None
        assert updated.stock_quantity == original - 3
    
    def test_can_decrement_to_zero(self, db_session, sample_menu_items):
        """Should allow decrementing to zero."""
        fries = sample_menu_items[3]
        assert fries.stock_quantity == 0
        
        # Need an item with stock to test this
        burger = sample_menu_items[0]
        updated = InventoryService.decrement_stock(db_session, burger.id, 10)
        
        assert updated.stock_quantity == 0
    
    def test_raises_error_when_insufficient_stock(self, db_session, sample_menu_items):
        """Should reject decrement that exceeds current stock."""
        pizza = sample_menu_items[1]
        assert pizza.stock_quantity == 2
        
        with pytest.raises(ValueError, match="Insufficient stock"):
            InventoryService.decrement_stock(db_session, pizza.id, 5)
    
    def test_raises_error_for_zero_decrement(self, db_session, sample_menu_items):
        """Should reject zero decrement amount."""
        burger = sample_menu_items[0]
        
        with pytest.raises(ValueError, match="must be positive"):
            InventoryService.decrement_stock(db_session, burger.id, 0)
    
    def test_raises_error_for_negative_decrement(self, db_session, sample_menu_items):
        """Should reject negative decrement amount."""
        burger = sample_menu_items[0]
        
        with pytest.raises(ValueError, match="must be positive"):
            InventoryService.decrement_stock(db_session, burger.id, -5)
    
    def test_returns_none_for_nonexistent_item(self, db_session):
        """Should return None when item doesn't exist."""
        updated = InventoryService.decrement_stock(db_session, 99999, 5)
        assert updated is None
    
    def test_multiple_decrements_accumulate(self, db_session, sample_menu_items):
        """Should accumulate multiple decrements."""
        burger = sample_menu_items[0]
        initial = burger.stock_quantity
        
        InventoryService.decrement_stock(db_session, burger.id, 2)
        db_session.refresh(burger)
        InventoryService.decrement_stock(db_session, burger.id, 1)
        db_session.refresh(burger)
        InventoryService.decrement_stock(db_session, burger.id, 3)
        db_session.refresh(burger)
        
        assert burger.stock_quantity == initial - 6


class TestCheckStockAvailability:
    """Test checking if stock is available."""
    
    def test_returns_true_when_sufficient_stock(self, db_session, sample_menu_items):
        """Should return True when enough stock exists."""
        burger = sample_menu_items[0]  # Has 10 items
        
        available = InventoryService.check_stock_availability(
            db_session,
            burger.id,
            5
        )
        
        assert available is True
    
    def test_returns_true_when_exact_quantity_available(self, db_session, sample_menu_items):
        """Should return True when exact quantity is available."""
        burger = sample_menu_items[0]  # Has 10 items
        
        available = InventoryService.check_stock_availability(
            db_session,
            burger.id,
            10
        )
        
        assert available is True
    
    def test_returns_false_when_insufficient_stock(self, db_session, sample_menu_items):
        """Should return False when insufficient stock."""
        burger = sample_menu_items[0]  # Has 10 items
        
        available = InventoryService.check_stock_availability(
            db_session,
            burger.id,
            15
        )
        
        assert available is False
    
    def test_returns_false_when_out_of_stock(self, db_session, sample_menu_items):
        """Should return False when item is out of stock."""
        fries = sample_menu_items[3]  # Has 0 items
        
        available = InventoryService.check_stock_availability(
            db_session,
            fries.id,
            1
        )
        
        assert available is False
    
    def test_returns_false_when_item_not_found(self, db_session):
        """Should return False when item doesn't exist."""
        available = InventoryService.check_stock_availability(
            db_session,
            99999,
            5
        )
        
        assert available is False
    
    def test_returns_true_for_zero_quantity_check(self, db_session, sample_menu_items):
        """Should return True when checking for zero quantity."""
        fries = sample_menu_items[3]  # Has 0 items
        
        available = InventoryService.check_stock_availability(
            db_session,
            fries.id,
            0
        )
        
        assert available is True


class TestGetLowStockItems:
    """Test identifying low-stock items."""
    
    def test_returns_items_below_threshold(self, db_session, sample_menu_items):
        """Should return items with stock below threshold."""
        low_stock = InventoryService.get_low_stock_items(db_session)
        
        # Pizza (2), Soda (5), and Fries (0) are at or below threshold (5)
        assert len(low_stock) == 3
        names = [item.name for item in low_stock]
        assert "Pizza" in names
        assert "Soda" in names
        assert "Fries" in names
    
    def test_includes_items_at_threshold(self, db_session, sample_menu_items):
        """Should include items exactly at threshold."""
        soda = sample_menu_items[2]  # stock=5, threshold=5
        
        low_stock = InventoryService.get_low_stock_items(db_session)
        
        assert any(item.id == soda.id for item in low_stock)
    
    def test_includes_out_of_stock_items(self, db_session, sample_menu_items):
        """Should include out-of-stock items."""
        fries = sample_menu_items[3]  # stock=0
        
        low_stock = InventoryService.get_low_stock_items(db_session)
        
        assert any(item.id == fries.id for item in low_stock)
    
    def test_excludes_items_above_threshold(self, db_session, sample_menu_items):
        """Should not include items above threshold."""
        burger = sample_menu_items[0]  # stock=10, threshold=5
        
        low_stock = InventoryService.get_low_stock_items(db_session)
        
        assert not any(item.id == burger.id for item in low_stock)
    
    def test_excludes_deleted_items(self, db_session, sample_menu_items):
        """Should not return deleted items even if low stock."""
        old_item = sample_menu_items[4]  # stock=1, threshold=5, deleted=True
        
        low_stock = InventoryService.get_low_stock_items(db_session)
        
        assert not any(item.id == old_item.id for item in low_stock)
    
    def test_returns_empty_when_no_low_stock(self, db_session):
        """Should return empty list when all items well-stocked."""
        # Add items above threshold
        item1 = MenuItem(
            name="Item1",
            description="Well stocked",
            price=Decimal("5.00"),
            category="Meals",
            stock_quantity=100,
            stock_threshold=10,
            is_available=True,
            is_deleted=False
        )
        item2 = MenuItem(
            name="Item2",
            description="Well stocked",
            price=Decimal("5.00"),
            category="Meals",
            stock_quantity=50,
            stock_threshold=10,
            is_available=True,
            is_deleted=False
        )
        db_session.add(item1)
        db_session.add(item2)
        db_session.commit()
        
        low_stock = InventoryService.get_low_stock_items(db_session)
        
        assert len(low_stock) == 0


class TestUpdateStockThreshold:
    """Test updating stock threshold."""
    
    def test_updates_threshold_value(self, db_session, sample_menu_items):
        """Should update stock threshold."""
        burger = sample_menu_items[0]
        original_threshold = burger.stock_threshold
        
        updated = InventoryService.update_stock_threshold(
            db_session,
            burger.id,
            15
        )
        
        assert updated is not None
        assert updated.stock_threshold == 15
        assert updated.stock_threshold != original_threshold
    
    def test_can_set_threshold_to_zero(self, db_session, sample_menu_items):
        """Should allow setting threshold to zero."""
        burger = sample_menu_items[0]
        
        updated = InventoryService.update_stock_threshold(db_session, burger.id, 0)
        
        assert updated is not None
        assert updated.stock_threshold == 0
    
    def test_raises_error_for_negative_threshold(self, db_session, sample_menu_items):
        """Should reject negative threshold values."""
        burger = sample_menu_items[0]
        
        with pytest.raises(ValueError, match="cannot be negative"):
            InventoryService.update_stock_threshold(db_session, burger.id, -5)
    
    def test_returns_none_for_nonexistent_item(self, db_session):
        """Should return None when item doesn't exist."""
        updated = InventoryService.update_stock_threshold(db_session, 99999, 10)
        assert updated is None
    
    def test_preserves_stock_quantity(self, db_session, sample_menu_items):
        """Should not affect stock quantity."""
        burger = sample_menu_items[0]
        original_stock = burger.stock_quantity
        
        InventoryService.update_stock_threshold(db_session, burger.id, 20)
        db_session.refresh(burger)
        
        assert burger.stock_quantity == original_stock
    
    def test_affects_low_stock_detection(self, db_session, sample_menu_items):
        """Should affect which items are considered low-stock."""
        burger = sample_menu_items[0]  # stock=10, currently threshold=5
        
        # Before: not low stock
        low_stock = InventoryService.get_low_stock_items(db_session)
        assert not any(item.id == burger.id for item in low_stock)
        
        # Update threshold to 15
        InventoryService.update_stock_threshold(db_session, burger.id, 15)
        
        # After: should be low stock (10 <= 15)
        low_stock = InventoryService.get_low_stock_items(db_session)
        assert any(item.id == burger.id for item in low_stock)
