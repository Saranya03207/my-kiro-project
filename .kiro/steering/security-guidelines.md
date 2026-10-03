# Security and Data Handling Guidelines

## Input Validation

### Backend Validation (Primary Defense)

**Always validate on the backend** - never trust client-side validation alone.

```python
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from typing import Optional

class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., max_length=500)
    price: Decimal = Field(..., ge=0.01, le=9999.99, decimal_places=2)
    category: str = Field(..., min_length=1, max_length=50)
    stock_quantity: int = Field(..., ge=0)
    stock_threshold: int = Field(5, ge=0)
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()
    
    @validator('price')
    def price_must_have_max_two_decimals(cls, v):
        if v.as_tuple().exponent < -2:
            raise ValueError('Price can have at most 2 decimal places')
        return v
```

### Input Sanitization

```python
import re
from html import escape

def sanitize_string(value: str) -> str:
    """
    Sanitize string input to prevent injection attacks.
    
    - Strip leading/trailing whitespace
    - Escape HTML entities
    - Remove null bytes
    - Limit length
    """
    if not isinstance(value, str):
        raise ValueError("Input must be a string")
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Strip whitespace
    value = value.strip()
    
    # Escape HTML entities (prevent XSS)
    value = escape(value)
    
    return value

def sanitize_search_query(query: str) -> str:
    """
    Sanitize search query for safe database operations.
    
    - Remove SQL special characters
    - Limit length
    - Strip whitespace
    """
    # Remove potentially dangerous characters
    query = re.sub(r'[;\'\"\\]', '', query)
    
    # Limit length
    query = query[:100]
    
    return query.strip()
```

### Frontend Validation (User Experience)

```javascript
// Validate before sending to backend
function validateMenuItem(item) {
  const errors = {};
  
  // Name validation
  if (!item.name || item.name.trim().length === 0) {
    errors.name = 'Name is required';
  } else if (item.name.length > 100) {
    errors.name = 'Name must be 100 characters or less';
  }
  
  // Price validation
  if (!item.price || item.price <= 0) {
    errors.price = 'Price must be greater than 0';
  } else if (!/^\d+(\.\d{1,2})?$/.test(item.price.toString())) {
    errors.price = 'Price must have at most 2 decimal places';
  }
  
  // Stock validation
  if (item.stock_quantity < 0) {
    errors.stock_quantity = 'Stock cannot be negative';
  }
  
  return errors;
}
```

## SQL Injection Prevention

### ALWAYS Use ORM

```python
# ❌ NEVER do this - vulnerable to SQL injection
def get_menu_item_unsafe(item_id: str):
    query = f"SELECT * FROM menu_items WHERE id = {item_id}"
    return db.execute(query)

# ❌ NEVER do this either
def search_menu_unsafe(search: str):
    query = f"SELECT * FROM menu_items WHERE name LIKE '%{search}%'"
    return db.execute(query)

# ✅ ALWAYS use ORM - safe from SQL injection
def get_menu_item_safe(item_id: int):
    return db.query(MenuItem).filter(MenuItem.id == item_id).first()

# ✅ ALWAYS use parameterized queries with ORM
def search_menu_safe(search: str):
    search_pattern = f"%{search}%"
    return db.query(MenuItem).filter(
        MenuItem.name.ilike(search_pattern)
    ).all()
```

### Use Transactions for Multi-Step Operations

```python
from sqlalchemy.exc import SQLAlchemyError

def create_order_safe(student_id: str, order_items: List[OrderItemCreate]):
    """
    Create order with transaction to ensure atomicity.
    All operations succeed or all fail together.
    """
    try:
        # Start transaction
        order = Order(
            student_id=student_id,
            total_price=calculate_total(order_items),
            status='pending'
        )
        db.add(order)
        db.flush()  # Get order ID without committing
        
        # Add order items and update stock
        for item_data in order_items:
            # Get menu item
            menu_item = db.query(MenuItem).filter(
                MenuItem.id == item_data.menu_item_id
            ).with_for_update().first()  # Lock row
            
            if not menu_item:
                raise ValueError(f"Menu item {item_data.menu_item_id} not found")
            
            if menu_item.stock_quantity < item_data.quantity:
                raise ValueError(
                    f"Insufficient stock for {menu_item.name}"
                )
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=menu_item.id,
                quantity=item_data.quantity,
                price_at_order_time=menu_item.price
            )
            db.add(order_item)
            
            # Update stock
            menu_item.stock_quantity -= item_data.quantity
        
        # Commit transaction
        db.commit()
        return order
        
    except SQLAlchemyError as e:
        # Rollback on any error
        db.rollback()
        logger.error(f"Failed to create order: {e}")
        raise
```

## Authentication and Authorization

### Session Management

```python
import secrets
from datetime import datetime, timedelta
from typing import Optional

class SessionService:
    """Handle user session creation and validation"""
    
    @staticmethod
    def create_session(user_id: str, role: str) -> Session:
        """
        Create a new user session with secure token.
        
        Args:
            user_id: User identifier
            role: User role ('student' or 'admin')
            
        Returns:
            Session object with token
        """
        # Generate cryptographically secure token
        token = secrets.token_urlsafe(32)
        
        # Set expiration (24 hours)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        session = Session(
            user_id=user_id,
            role=role,
            token=token,
            expires_at=expires_at
        )
        
        db.add(session)
        db.commit()
        
        return session
    
    @staticmethod
    def validate_session(token: str) -> Optional[Session]:
        """
        Validate session token and check expiration.
        
        Args:
            token: Session token from request
            
        Returns:
            Session object if valid, None otherwise
        """
        session = db.query(Session).filter(
            Session.token == token
        ).first()
        
        if not session:
            return None
        
        # Check expiration
        if session.expires_at < datetime.utcnow():
            # Delete expired session
            db.delete(session)
            db.commit()
            return None
        
        return session
    
    @staticmethod
    def invalidate_session(token: str) -> bool:
        """
        Invalidate (delete) a session.
        
        Args:
            token: Session token to invalidate
            
        Returns:
            True if session was deleted, False otherwise
        """
        session = db.query(Session).filter(
            Session.token == token
        ).first()
        
        if session:
            db.delete(session)
            db.commit()
            return True
        
        return False
```

### Authorization Middleware

```python
from fastapi import Depends, HTTPException, Header
from typing import Optional

def get_current_user(
    authorization: Optional[str] = Header(None)
) -> Session:
    """
    Extract and validate session token from Authorization header.
    
    Raises:
        HTTPException: 401 if token is missing or invalid
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    
    token = parts[1]
    
    # Validate session
    session = SessionService.validate_session(token)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )
    
    return session

def require_admin(
    current_user: Session = Depends(get_current_user)
) -> Session:
    """
    Require admin role for endpoint access.
    
    Raises:
        HTTPException: 403 if user is not admin
    """
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return current_user

# Usage in routes
@router.get("/admin/orders")
async def get_all_orders(
    admin: Session = Depends(require_admin)
):
    """Admin-only endpoint"""
    return order_service.get_all_orders()
```

### Frontend Session Handling

```javascript
// Session storage keys
const STORAGE_KEYS = {
  SESSION_TOKEN: 'canteen_session_token',
  USER_ID: 'canteen_user_id',
  USER_ROLE: 'canteen_user_role'
};

class AuthService {
  /**
   * Store session after successful login
   */
  static storeSession(token, userId, role) {
    sessionStorage.setItem(STORAGE_KEYS.SESSION_TOKEN, token);
    sessionStorage.setItem(STORAGE_KEYS.USER_ID, userId);
    sessionStorage.setItem(STORAGE_KEYS.USER_ROLE, role);
  }
  
  /**
   * Get current session token
   */
  static getToken() {
    return sessionStorage.getItem(STORAGE_KEYS.SESSION_TOKEN);
  }
  
  /**
   * Check if user is authenticated
   */
  static isAuthenticated() {
    return !!this.getToken();
  }
  
  /**
   * Check if current user is admin
   */
  static isAdmin() {
    return sessionStorage.getItem(STORAGE_KEYS.USER_ROLE) === 'admin';
  }
  
  /**
   * Clear session (logout)
   */
  static clearSession() {
    sessionStorage.removeItem(STORAGE_KEYS.SESSION_TOKEN);
    sessionStorage.removeItem(STORAGE_KEYS.USER_ID);
    sessionStorage.removeItem(STORAGE_KEYS.USER_ROLE);
  }
  
  /**
   * Redirect to login if not authenticated
   */
  static requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = '/index.html';
      return false;
    }
    return true;
  }
}

// Check auth on page load
document.addEventListener('DOMContentLoaded', () => {
  AuthService.requireAuth();
});
```

## Secure Configuration

### Environment Variables

```python
# config.py
from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    Never hardcode secrets in code.
    """
    
    # Database
    database_url: str = "sqlite:///./canteen.db"
    
    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    
    # Security
    secret_key: str = "CHANGE_THIS_IN_PRODUCTION"
    session_expiry_hours: int = 24
    rate_limit_per_minute: int = 100
    
    # AI Service (optional, sensitive)
    ai_service_url: Optional[str] = None
    ai_service_api_key: Optional[str] = None
    ai_service_timeout: int = 5
    ai_service_enabled: bool = True
    
    # CORS
    cors_origins: list = ["http://localhost:3000"]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/canteen.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Validate critical settings on startup
def validate_config():
    """Validate configuration and fail fast if misconfigured"""
    if settings.secret_key == "CHANGE_THIS_IN_PRODUCTION":
        raise ValueError(
            "SECRET_KEY must be changed in production. "
            "Set SECRET_KEY environment variable."
        )
    
    if settings.ai_service_enabled and not settings.ai_service_url:
        logger.warning("AI service enabled but URL not configured. Disabling AI.")
        settings.ai_service_enabled = False
```

### .env.example Template

```bash
# .env.example - Copy to .env and fill in values

# Database
DATABASE_URL=sqlite:///./canteen.db

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# Security
SECRET_KEY=generate-a-secure-random-key-here
SESSION_EXPIRY_HOURS=24
RATE_LIMIT_PER_MINUTE=100

# AI Service (Optional)
AI_SERVICE_URL=https://api.example.com/ai/chat
AI_SERVICE_API_KEY=your-api-key-here
AI_SERVICE_TIMEOUT=5
AI_SERVICE_ENABLED=true

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/canteen.log
```

## Never Expose Secrets

### ❌ Bad Examples

```python
# NEVER hardcode secrets
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "mypassword123"

# NEVER log secrets
logger.info(f"API key: {api_key}")
logger.debug(f"User token: {session.token}")

# NEVER return secrets in responses
return {
    "user": user.name,
    "session_token": session.token,  # ❌ Don't expose
    "api_key": settings.ai_service_api_key  # ❌ NEVER
}

# NEVER commit .env files
# Add to .gitignore:
# .env
# *.key
# *.pem
```

### ✅ Good Examples

```python
# Load from environment
from os import getenv
API_KEY = getenv("AI_SERVICE_API_KEY")

# Log without exposing secrets
logger.info(f"API key: ***{api_key[-4:]}")  # Show last 4 chars only
logger.info(f"Session created for user: {session.user_id}")

# Never return secrets
return {
    "user": user.name,
    "session_expires_at": session.expires_at  # ✅ Safe metadata
}

# Always ignore secret files
# .gitignore:
.env
.env.local
*.key
*.pem
secrets/
```

## Rate Limiting

```python
from fastapi import Request
from collections import defaultdict
from datetime import datetime, timedelta
import time

class RateLimiter:
    """Simple rate limiter based on IP address"""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def is_allowed(self, ip_address: str) -> bool:
        """
        Check if request from IP is allowed.
        
        Args:
            ip_address: Client IP address
            
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        now = time.time()
        minute_ago = now - 60
        
        # Remove old requests
        self.requests[ip_address] = [
            req_time for req_time in self.requests[ip_address]
            if req_time > minute_ago
        ]
        
        # Check if limit exceeded
        if len(self.requests[ip_address]) >= self.requests_per_minute:
            return False
        
        # Add current request
        self.requests[ip_address].append(now)
        return True

# Create rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=100)

# Middleware to enforce rate limiting
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "details": {"retry_after": 60}
                }
            }
        )
    
    response = await call_next(request)
    return response
```

## Security Checklist

### Before Deployment

- [ ] All secrets loaded from environment variables (not hardcoded)
- [ ] `.env` file added to `.gitignore`
- [ ] SECRET_KEY changed from default value
- [ ] All user input validated with Pydantic
- [ ] No raw SQL queries (only ORM)
- [ ] SQL injection tested (parameterized queries only)
- [ ] XSS prevention (HTML escaping on output)
- [ ] CSRF protection (if using forms with state-changing operations)
- [ ] Rate limiting enabled
- [ ] CORS configured to allow only trusted origins
- [ ] Session tokens use cryptographically secure generation
- [ ] Session expiration enforced
- [ ] Admin endpoints require admin role
- [ ] Error messages don't expose internal details
- [ ] Logging doesn't include secrets or tokens
- [ ] HTTPS enabled in production
- [ ] Database backups configured
- [ ] Security headers set (CSP, X-Content-Type-Options, etc.)

### Regular Security Reviews

- [ ] Review and rotate secrets regularly
- [ ] Update dependencies for security patches
- [ ] Audit logs for suspicious activity
- [ ] Test rate limiting effectiveness
- [ ] Review admin access logs
- [ ] Check for exposed secrets in git history
- [ ] Verify CORS configuration
- [ ] Test authentication and authorization flows
