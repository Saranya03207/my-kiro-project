"""
Integration tests for authentication routes.
Tests login and logout endpoints with actual HTTP requests.
"""
import pytest
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database import Base, get_db


@pytest.fixture(scope="function")
def client():
    """Create test client with test database."""
    # Create test database engine with shared cache to ensure single database instance
    # file::memory:?cache=shared creates a named in-memory database that can be accessed
    # by multiple connections, unlike :memory: which creates separate databases per connection
    test_engine = create_engine(
        "sqlite:///file::memory:?cache=shared&uri=true",
        connect_args={"check_same_thread": False, "uri": True}
    )
    
    # Import all models to ensure they're registered with Base
    from backend.models.menu_item import MenuItem
    from backend.models.order import Order
    from backend.models.order_item import OrderItem
    from backend.models.session import Session
    
    # Create all tables in test database
    Base.metadata.create_all(bind=test_engine)
    
    # Create session factory for this test
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    def override_get_db():
        """Override database dependency to use test database."""
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    # CRITICAL: Replace the module-level engine and SessionLocal BEFORE importing main
    import backend.database
    original_engine = backend.database.engine
    original_sessionlocal = backend.database.SessionLocal
    original_init_db = backend.database.init_db
    
    backend.database.engine = test_engine
    backend.database.SessionLocal = TestingSessionLocal
    # Replace init_db with a no-op since we already created tables
    backend.database.init_db = lambda: None
    
    # Now import app - the lifespan will use our patched init_db
    # If backend.main is already imported, we need to reload it
    if 'backend.main' in sys.modules:
        import importlib
        import backend.main
        importlib.reload(backend.main)
        app = backend.main.app
    else:
        from backend.main import app
    
    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    
    # Restore original database configuration
    backend.database.engine = original_engine
    backend.database.SessionLocal = original_sessionlocal
    backend.database.init_db = original_init_db


class TestLoginEndpoint:
    """Test POST /api/v1/auth/login endpoint."""
    
    def test_login_with_student_role(self, client):
        """Should create session for student."""
        response = client.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user_id"] == "S001"
        assert data["role"] == "student"
        assert "expires_at" in data
    
    def test_login_with_admin_role(self, client):
        """Should create session for admin."""
        response = client.post(
            "/api/v1/auth/login",
            json={"user_id": "admin123", "role": "admin"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["user_id"] == "admin123"
        assert data["role"] == "admin"
        assert "expires_at" in data
    
    def test_login_with_invalid_role(self, client):
        """Should reject login with invalid role."""
        response = client.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "invalid"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_with_empty_user_id(self, client):
        """Should reject login with empty user_id."""
        response = client.post(
            "/api/v1/auth/login",
            json={"user_id": "", "role": "student"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_with_whitespace_only_user_id(self, client):
        """Should reject login with whitespace-only user_id."""
        response = client.post(
            "/api/v1/auth/login",
            json={"user_id": "   ", "role": "student"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_with_long_user_id(self, client):
        """Should accept user_id up to 50 characters."""
        user_id = "S" * 50
        response = client.post(
            "/api/v1/auth/login",
            json={"user_id": user_id, "role": "student"}
        )
        
        assert response.status_code == 200
        assert response.json()["user_id"] == user_id
    
    def test_login_with_too_long_user_id(self, client):
        """Should reject user_id over 50 characters."""
        user_id = "S" * 51
        response = client.post(
            "/api/v1/auth/login",
            json={"user_id": user_id, "role": "student"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_missing_user_id(self, client):
        """Should reject login missing user_id field."""
        response = client.post(
            "/api/v1/auth/login",
            json={"role": "student"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_missing_role(self, client):
        """Should reject login missing role field."""
        response = client.post(
            "/api/v1/auth/login",
            json={"user_id": "S001"}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_login_with_malformed_json(self, client):
        """Should reject malformed JSON."""
        response = client.post(
            "/api/v1/auth/login",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_multiple_logins_generate_different_tokens(self, client):
        """Multiple logins should generate different tokens."""
        response1 = client.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        response2 = client.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        token1 = response1.json()["token"]
        token2 = response2.json()["token"]
        
        assert token1 != token2


class TestLogoutEndpoint:
    """Test POST /api/v1/auth/logout endpoint."""
    
    def test_logout_with_valid_token(self, client):
        """Should successfully logout with valid token."""
        # First login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        # Then logout
        logout_response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert logout_response.status_code == 200
        assert logout_response.json()["message"] == "Logged out successfully"
    
    def test_logout_without_authorization_header(self, client):
        """Should reject logout without authorization header."""
        response = client.post("/api/v1/auth/logout")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
    
    def test_logout_with_invalid_token(self, client):
        """Should reject logout with invalid token."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
    
    def test_logout_with_malformed_authorization_header(self, client):
        """Should reject malformed authorization header."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "InvalidFormat token123"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
    
    def test_logout_with_missing_bearer_prefix(self, client):
        """Should reject authorization header without Bearer prefix."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "token123"}
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]
    
    def test_logout_twice_with_same_token(self, client):
        """Should fail second logout with same token."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        # First logout
        logout1 = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert logout1.status_code == 200
        
        # Second logout with same token
        logout2 = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert logout2.status_code == 404  # Session not found
    
    def test_cannot_use_token_after_logout(self, client):
        """Token should be invalid after logout."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token = login_response.json()["token"]
        
        # Logout
        client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Try to use token again
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404


class TestAuthenticationFlow:
    """Test complete authentication workflows."""
    
    def test_login_and_logout_flow(self, client):
        """Test complete login and logout flow."""
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["token"]
        assert token
        
        # Logout
        logout_response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert logout_response.status_code == 200
    
    def test_multiple_users_different_sessions(self, client):
        """Different users should have different sessions."""
        # User 1 login
        response1 = client.post(
            "/api/v1/auth/login",
            json={"user_id": "S001", "role": "student"}
        )
        token1 = response1.json()["token"]
        
        # User 2 login
        response2 = client.post(
            "/api/v1/auth/login",
            json={"user_id": "S002", "role": "student"}
        )
        token2 = response2.json()["token"]
        
        assert token1 != token2
        
        # User 1 logout shouldn't affect User 2
        client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token1}"}
        )
        
        # User 2 should still be able to logout
        logout2 = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token2}"}
        )
        assert logout2.status_code == 200
