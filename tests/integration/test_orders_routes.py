"""
Integration tests for orders routes.
Tests student order placement and admin order management.
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
def client_with_orders():
    """Create test client with test database and sample menu items."""
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
            description="Cheese pizza",
            price=Decimal("12.99"),
            category="Meals",
            stock_quantity=5,
            stock_threshold=2,
            is_available=True
        ),
        MenuItem(
            name="Fries",
            description="Crispy fries",
            price=Decimal("3.99"),
            category="Snacks",
            stock_quantity=0,
            stock_threshold=5,
            is_available=True
        ),
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


class TestCreateOrder:
    """Test POST /api/v1/orders endpoint."""
    
    def test_create_order_success(self, client_with_orders):
        """Should create order with valid items."""
        # Login
        login_response = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        # Create order
        response = client_with_orders.post(
            "/api/v1/orders",
            json={
                "items": [
                    {"menu_item_id": 1, "quantity": 2}
                ]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        order = response.json()
        
        assert order["student_id"] == "S001"
        assert order["status"] == "pending"
        assert order["total_price"] == "19.98"
        assert len(order["items"]) == 1
        assert order["items"][0]["menu_item_id"] == 1
        assert order["items"][0]["quantity"] == 2
    
    def test_create_order_multiple_items(self, client_with_orders):
        """Should create order with multiple items."""
        login_response = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_orders.post(
            "/api/v1/orders",
            json={
                "items": [
                    {"menu_item_id": 1, "quantity": 1},
                    {"menu_item_id": 2, "quantity": 1}
                ]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 201
        order = response.json()
        
        assert len(order["items"]) == 2
        # Total: 9.99 + 12.99 = 22.98
        assert order["total_price"] == "22.98"
    
    def test_create_order_insufficient_stock(self, client_with_orders):
        """Should fail if insufficient stock."""
        login_response = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        # Try to order 15 burgers when only 10 available
        response = client_with_orders.post(
            "/api/v1/orders",
            json={
                "items": [
                    {"menu_item_id": 1, "quantity": 15}
                ]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]["error"]["message"]
    
    def test_create_order_no_stock_available(self, client_with_orders):
        """Should fail if item has zero stock."""
        login_response = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        # Try to order Fries which has 0 stock
        response = client_with_orders.post(
            "/api/v1/orders",
            json={
                "items": [
                    {"menu_item_id": 3, "quantity": 1}
                ]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]["error"]["message"]
    
    def test_create_order_invalid_item(self, client_with_orders):
        """Should fail with non-existent item."""
        login_response = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_orders.post(
            "/api/v1/orders",
            json={
                "items": [
                    {"menu_item_id": 999, "quantity": 1}
                ]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 400
    
    def test_create_order_no_items(self, client_with_orders):
        """Should fail with empty items list."""
        login_response = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_orders.post(
            "/api/v1/orders",
            json={"items": []},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_order_without_authentication(self, client_with_orders):
        """Should require authentication."""
        response = client_with_orders.post(
            "/api/v1/orders",
            json={"items": [{"menu_item_id": 1, "quantity": 1}]}
        )
        
        assert response.status_code == 401


class TestGetOrder:
    """Test GET /api/v1/orders/{order_id} endpoint."""
    
    def test_get_order_success(self, client_with_orders):
        """Should return order details."""
        login_response = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        # Create order
        create_response = client_with_orders.post(
            "/api/v1/orders",
            json={"items": [{"menu_item_id": 1, "quantity": 1}]},
            headers={"Authorization": f"Bearer {token}"}
        )
        order_id = create_response.json()["id"]
        
        # Get order
        response = client_with_orders.get(
            f"/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        order = response.json()
        assert order["id"] == order_id
        assert order["student_id"] == "S001"
    
    def test_get_order_not_found(self, client_with_orders):
        """Should return 404 for non-existent order."""
        login_response = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_orders.get(
            "/api/v1/orders/999",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
    
    def test_student_cannot_see_other_orders(self, client_with_orders):
        """Students should only see their own orders."""
        # Student 1 creates order
        login1 = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token1 = login1.json()["token"]
        
        create_response = client_with_orders.post(
            "/api/v1/orders",
            json={"items": [{"menu_item_id": 1, "quantity": 1}]},
            headers={"Authorization": f"Bearer {token1}"}
        )
        order_id = create_response.json()["id"]
        
        # Student 2 tries to view Student 1's order
        login2 = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S002", "role": "student"}
        )
        token2 = login2.json()["token"]
        
        response = client_with_orders.get(
            f"/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response.status_code == 403


class TestGetOrderHistory:
    """Test GET /api/v1/orders/history endpoint."""
    
    def test_get_order_history(self, client_with_orders):
        """Should return student's order history."""
        login_response = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        # Create two orders
        client_with_orders.post(
            "/api/v1/orders",
            json={"items": [{"menu_item_id": 1, "quantity": 1}]},
            headers={"Authorization": f"Bearer {token}"}
        )
        client_with_orders.post(
            "/api/v1/orders",
            json={"items": [{"menu_item_id": 2, "quantity": 1}]},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Get history
        response = client_with_orders.get(
            "/api/v1/orders/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) == 2
    
    def test_get_order_history_empty(self, client_with_orders):
        """Should return empty list if no orders."""
        login_response = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S003", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_orders.get(
            "/api/v1/orders/history",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) == 0


class TestAdminGetAllOrders:
    """Test GET /api/v1/admin/orders endpoint."""
    
    def test_admin_get_all_orders(self, client_with_orders):
        """Admin should see all orders."""
        # Student creates order
        student_login = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        student_token = student_login.json()["token"]
        
        client_with_orders.post(
            "/api/v1/orders",
            json={"items": [{"menu_item_id": 1, "quantity": 1}]},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        # Admin gets all orders
        admin_login = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]
        
        response = client_with_orders.get(
            "/api/v1/admin/orders",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) >= 1
    
    def test_student_cannot_access_admin_orders(self, client_with_orders):
        """Students cannot access admin endpoints."""
        login_response = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        response = client_with_orders.get(
            "/api/v1/admin/orders",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403


class TestAdminUpdateOrderStatus:
    """Test PATCH /api/v1/admin/orders/{order_id}/status endpoint."""
    
    def test_admin_update_order_status(self, client_with_orders):
        """Admin should update order status."""
        # Create order
        student_login = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        student_token = student_login.json()["token"]
        
        create_response = client_with_orders.post(
            "/api/v1/orders",
            json={"items": [{"menu_item_id": 1, "quantity": 1}]},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        order_id = create_response.json()["id"]
        
        # Admin updates status
        admin_login = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]
        
        response = client_with_orders.patch(
            f"/api/v1/admin/orders/{order_id}/status?new_status=preparing",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        order = response.json()
        assert order["status"] == "preparing"
    
    def test_invalid_status_transition(self, client_with_orders):
        """Should fail on invalid status transition."""
        # Create and complete order
        student_login = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        student_token = student_login.json()["token"]
        
        create_response = client_with_orders.post(
            "/api/v1/orders",
            json={"items": [{"menu_item_id": 1, "quantity": 1}]},
            headers={"Authorization": f"Bearer {student_token}"}
        )
        order_id = create_response.json()["id"]
        
        admin_login = client_with_orders.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]
        
        # Try invalid transition: pending -> completed (should go through intermediate states)
        response = client_with_orders.patch(
            f"/api/v1/admin/orders/{order_id}/status?new_status=completed",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 400
        assert "Invalid status transition" in response.json()["detail"]["error"]["message"]
