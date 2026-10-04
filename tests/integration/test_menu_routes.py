"""
Integration tests for menu routes.
Tests menu browsing endpoints for students.
"""
import pytest
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, get_db
from backend.models.menu_item import MenuItem
from decimal import Decimal


@pytest.fixture(scope="function")
def client_with_menu():
    """Create test client with test database and sample menu items."""
    # Create test database
    test_engine = create_engine(
        "sqlite:///file::memory:?cache=shared&uri=true",
        connect_args={"check_same_thread": False, "uri": True}
    )
    
    # Import all models
    from backend.models.menu_item import MenuItem
    from backend.models.order import Order
    from backend.models.order_item import OrderItem
    from backend.models.session import Session
    
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # Patch database
    import backend.database
    original_engine = backend.database.engine
    original_sessionlocal = backend.database.SessionLocal
    original_init_db = backend.database.init_db
    
    backend.database.engine = test_engine
    backend.database.SessionLocal = TestingSessionLocal
    backend.database.init_db = lambda: None
    
    if 'backend.main' in sys.modules:
        import importlib
        import backend.main
        importlib.reload(backend.main)
        app = backend.main.app
    else:
        from backend.main import app
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Add sample menu items
    db = TestingSessionLocal()
    menu_items = [
        MenuItem(
            name="Burger",
            description="Delicious beef burger",
            price=Decimal("9.99"),
            category="Meals",
            stock_quantity=10,
            stock_threshold=2,
            is_available=True
        ),
        MenuItem(
            name="Pizza",
            description="Cheese pizza with toppings",
            price=Decimal("12.99"),
            category="Meals",
            stock_quantity=5,
            stock_threshold=2,
            is_available=True
        ),
        MenuItem(
            name="Fries",
            description="Crispy french fries",
            price=Decimal("3.99"),
            category="Snacks",
            stock_quantity=20,
            stock_threshold=5,
            is_available=True
        ),
        MenuItem(
            name="Soda",
            description="Cold soda drink",
            price=Decimal("2.99"),
            category="Beverages",
            stock_quantity=30,
            stock_threshold=10,
            is_available=True
        ),
        MenuItem(
            name="Salad",
            description="Fresh garden salad",
            price=Decimal("7.99"),
            category="Meals",
            stock_quantity=0,
            stock_threshold=5,
            is_available=False  # Unavailable
        )
    ]
    for item in menu_items:
        db.add(item)
    db.commit()
    db.close()
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    backend.database.engine = original_engine
    backend.database.SessionLocal = original_sessionlocal
    backend.database.init_db = original_init_db


class TestGetMenuItems:
    """Test GET /api/v1/menu/items endpoint."""
    
    def test_get_all_menu_items(self, client_with_menu):
        """Should return all available menu items."""
        # First login
        login_response = client_with_menu.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        # Get menu
        response = client_with_menu.get(
            "/api/v1/menu/items",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        items = response.json()
        
        # Should have 4 available items (Salad is unavailable)
        assert len(items) == 4
        
        # Check for expected items
        names = [item["name"] for item in items]
        assert "Burger" in names
        assert "Pizza" in names
        assert "Fries" in names
        assert "Soda" in names
        assert "Salad" not in names  # Unavailable should not be shown
    
    def test_menu_items_sorted_by_category_and_name(self, client_with_menu):
        """Menu items should be sorted by category then name."""
        login_response = client_with_menu.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_menu.get(
            "/api/v1/menu/items",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        items = response.json()
        
        # Items should be sorted: Beverages, Meals, Snacks
        categories = [item["category"] for item in items]
        assert categories == ["Beverages", "Meals", "Meals", "Snacks"]
    
    def test_search_menu_items_by_name(self, client_with_menu):
        """Should search and filter by item name."""
        login_response = client_with_menu.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_menu.get(
            "/api/v1/menu/items?search=burge",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        items = response.json()
        
        assert len(items) == 1
        assert items[0]["name"] == "Burger"
    
    def test_search_menu_items_by_description(self, client_with_menu):
        """Should search in description."""
        login_response = client_with_menu.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_menu.get(
            "/api/v1/menu/items?search=crispy",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        items = response.json()
        
        assert len(items) == 1
        assert items[0]["name"] == "Fries"
    
    def test_filter_menu_items_by_category(self, client_with_menu):
        """Should filter by category."""
        login_response = client_with_menu.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_menu.get(
            "/api/v1/menu/items?category=Meals",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        items = response.json()
        
        assert len(items) == 2
        assert all(item["category"] == "Meals" for item in items)
    
    def test_search_and_filter_combined(self, client_with_menu):
        """Should apply both search and filter."""
        login_response = client_with_menu.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_menu.get(
            "/api/v1/menu/items?search=p&category=Meals",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        items = response.json()
        
        assert len(items) == 1
        assert items[0]["name"] == "Pizza"
    
    def test_get_menu_without_authentication(self, client_with_menu):
        """Should require authentication."""
        response = client_with_menu.get("/api/v1/menu/items")
        assert response.status_code == 401


class TestGetMenuItem:
    """Test GET /api/v1/menu/items/{item_id} endpoint."""
    
    def test_get_menu_item_by_id(self, client_with_menu):
        """Should return menu item details by ID."""
        login_response = client_with_menu.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_menu.get(
            "/api/v1/menu/items/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        item = response.json()
        
        assert item["id"] == 1
        assert item["name"] == "Burger"
        assert item["price"] == "9.99"
        assert item["category"] == "Meals"
        assert item["stock_quantity"] == 10
    
    def test_get_menu_item_not_found(self, client_with_menu):
        """Should return 404 for non-existent item."""
        login_response = client_with_menu.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_menu.get(
            "/api/v1/menu/items/999",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    def test_get_unavailable_menu_item(self, client_with_menu):
        """Should not return unavailable items."""
        login_response = client_with_menu.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        # Salad is item 5 and unavailable
        response = client_with_menu.get(
            "/api/v1/menu/items/5",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    def test_get_menu_item_without_authentication(self, client_with_menu):
        """Should require authentication."""
        response = client_with_menu.get("/api/v1/menu/items/1")
        assert response.status_code == 401
