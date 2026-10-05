"""
Integration tests for admin routes.
Tests menu management, inventory management, and analytics endpoints.
"""
import pytest
import sys
import io
import os
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, get_db
from backend.models.menu_item import MenuItem
from decimal import Decimal


@pytest.fixture(scope="function")
def client_with_admin():
    """Create test client with test database and admin access."""
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
            description="Beef burger",
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
            stock_quantity=1,
            stock_threshold=2,
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


class TestCreateMenuItem:
    """Test POST /api/v1/admin/menu/items endpoint."""

    def test_create_menu_item_success(self, client_with_admin):
        """Should create menu item."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        response = client_with_admin.post(
            "/api/v1/admin/menu/items",
            json={
                "name": "Sandwich",
                "description": "Turkey sandwich",
                "price": "6.99",
                "category": "Meals",
                "stock_quantity": 15
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 201
        item = response.json()
        assert item["name"] == "Sandwich"
        assert item["price"] == "6.99"
        assert item["is_available"] == True

    def test_create_duplicate_item_name(self, client_with_admin):
        """Should fail with duplicate name."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        response = client_with_admin.post(
            "/api/v1/admin/menu/items",
            json={
                "name": "Burger",
                "description": "Another burger",
                "price": "8.99",
                "category": "Meals",
                "stock_quantity": 5
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 400

    def test_student_cannot_create_menu_item(self, client_with_admin):
        """Students cannot create menu items."""
        student_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        student_token = student_login.json()["token"]

        response = client_with_admin.post(
            "/api/v1/admin/menu/items",
            json={
                "name": "Test",
                "description": "Test item",
                "price": "5.99",
                "category": "Meals",
                "stock_quantity": 10
            },
            headers={"Authorization": f"Bearer {student_token}"}
        )

        assert response.status_code == 403


class TestUpdateMenuItem:
    """Test PUT /api/v1/admin/menu/items/{item_id} endpoint."""

    def test_update_menu_item(self, client_with_admin):
        """Should update menu item."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        response = client_with_admin.put(
            "/api/v1/admin/menu/items/1",
            json={
                "price": "10.99",
                "description": "Deluxe beef burger"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        item = response.json()
        assert item["price"] == "10.99"
        assert item["description"] == "Deluxe beef burger"
        assert item["name"] == "Burger"  # Unchanged

    def test_update_item_not_found(self, client_with_admin):
        """Should return 404 for non-existent item."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        response = client_with_admin.put(
            "/api/v1/admin/menu/items/999",
            json={"price": "10.99"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 404


class TestToggleMenuItemAvailability:
    """Test PATCH /api/v1/admin/menu/items/{item_id}/availability endpoint."""

    def test_toggle_availability(self, client_with_admin):
        """Should toggle availability."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        response = client_with_admin.patch(
            "/api/v1/admin/menu/items/1/availability",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        item = response.json()
        assert item["is_available"] == False

        # Toggle again
        response = client_with_admin.patch(
            "/api/v1/admin/menu/items/1/availability",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        item = response.json()
        assert item["is_available"] == True


class TestDeleteMenuItem:
    """Test DELETE /api/v1/admin/menu/items/{item_id} endpoint."""

    def test_delete_menu_item(self, client_with_admin):
        """Should soft delete menu item."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        response = client_with_admin.delete(
            "/api/v1/admin/menu/items/1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 204


class TestGetInventory:
    """Test GET /api/v1/admin/inventory endpoint."""

    def test_get_inventory(self, client_with_admin):
        """Should return all stock levels."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        response = client_with_admin.get(
            "/api/v1/admin/inventory",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        inventory = response.json()

        assert len(inventory) >= 2
        assert all("stock_quantity" in item for item in inventory)


class TestUpdateInventory:
    """Test PUT /api/v1/admin/inventory/{item_id} endpoint."""

    def test_update_stock_quantity(self, client_with_admin):
        """Should update stock quantity."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        response = client_with_admin.put(
            "/api/v1/admin/inventory/1?quantity=20",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        item = response.json()
        assert item["stock_quantity"] == 20


class TestGetLowStockItems:
    """Test GET /api/v1/admin/inventory/low-stock endpoint."""

    def test_get_low_stock_items(self, client_with_admin):
        """Should return items below threshold."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        response = client_with_admin.get(
            "/api/v1/admin/inventory/low-stock",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        items = response.json()

        # Pizza has stock=1, threshold=2, so it should be in low-stock
        assert any(item["name"] == "Pizza" for item in items)


class TestUpdateStockThreshold:
    """Test PUT /api/v1/admin/inventory/{item_id}/threshold endpoint."""

    def test_update_stock_threshold(self, client_with_admin):
        """Should update stock threshold."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        response = client_with_admin.put(
            "/api/v1/admin/inventory/1/threshold?threshold=5",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        item = response.json()
        assert item["stock_threshold"] == 5


class TestGetDailySales:
    """Test GET /api/v1/admin/analytics/sales/daily endpoint."""

    def test_get_daily_sales(self, client_with_admin):
        """Should return daily sales statistics."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        response = client_with_admin.get(
            "/api/v1/admin/analytics/sales/daily",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        sales = response.json()

        assert "date" in sales
        assert "total_revenue" in sales
        assert "order_count" in sales
        assert "average_order_value" in sales


class TestGetSalesByDateRange:
    """Test GET /api/v1/admin/analytics/sales/range endpoint."""

    def test_get_sales_by_date_range(self, client_with_admin):
        """Should return sales for date range."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        today = date.today()
        response = client_with_admin.get(
            f"/api/v1/admin/analytics/sales/range?start_date={today}&end_date={today}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        sales_list = response.json()

        assert isinstance(sales_list, list)
        assert len(sales_list) >= 1


class TestGetPopularItems:
    """Test GET /api/v1/admin/analytics/popular-items endpoint."""

    def test_get_popular_items(self, client_with_admin):
        """Should return popular items."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        response = client_with_admin.get(
            "/api/v1/admin/analytics/popular-items",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        items = response.json()

        assert isinstance(items, list)
        for item in items:
            assert "menu_item_id" in item
            assert "name" in item
            assert "order_count" in item
            assert "popularity_score" in item


class TestAdminAuthorization:
    """Test admin authorization across endpoints."""

    def test_student_cannot_access_admin_menu_endpoints(self, client_with_admin):
        """Students cannot access admin menu endpoints."""
        student_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        student_token = student_login.json()["token"]

        endpoints = [
            ("/api/v1/admin/menu/items", "POST"),
            ("/api/v1/admin/inventory", "GET"),
            ("/api/v1/admin/analytics/sales/daily", "GET"),
        ]

        for endpoint, method in endpoints:
            if method == "GET":
                response = client_with_admin.get(
                    endpoint,
                    headers={"Authorization": f"Bearer {student_token}"}
                )
            else:
                response = client_with_admin.post(
                    endpoint,
                    json={},
                    headers={"Authorization": f"Bearer {student_token}"}
                )

            assert response.status_code == 403, f"Expected 403 for {method} {endpoint}"


class TestUploadFoodImage:
    """Test POST /api/v1/admin/menu/upload-image endpoint."""

    def test_upload_valid_image(self, client_with_admin):
        """Should upload a valid image file."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        png_data = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        files = {"file": ("test.png", io.BytesIO(png_data), "image/png")}

        response = client_with_admin.post(
            "/api/v1/admin/menu/upload-image",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "image_url" in data
        assert data["image_url"].startswith("assets/food/")

        file_path = os.path.join("frontend", data["image_url"])
        if os.path.exists(file_path):
            os.remove(file_path)

    def test_upload_invalid_type(self, client_with_admin):
        """Should reject invalid file types."""
        admin_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        admin_token = admin_login.json()["token"]

        files = {"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")}
        response = client_with_admin.post(
            "/api/v1/admin/menu/upload-image",
            files=files,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400
        assert response.json()["detail"]["error"]["code"] == "INVALID_IMAGE_TYPE"

    def test_upload_student_forbidden(self, client_with_admin):
        """Students cannot upload food images."""
        student_login = client_with_admin.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        student_token = student_login.json()["token"]

        files = {"file": ("test.png", io.BytesIO(b"data"), "image/png")}
        response = client_with_admin.post(
            "/api/v1/admin/menu/upload-image",
            files=files,
            headers={"Authorization": f"Bearer {student_token}"}
        )
        assert response.status_code == 403
