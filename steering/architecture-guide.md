# Architecture Guide - Smart Canteen Development

## Backend Architecture Overview

The Smart Canteen Manager backend is built with **FastAPI**, **SQLAlchemy ORM**, and **SQLite**. It strictly follows a layered architectural pattern where route handlers remain thin HTTP adapters, and domain logic is encapsulated inside dedicated services.

```
backend/
├── main.py                     # FastAPI application setup, CORS, lifespan, router inclusion
├── config.py                   # Pydantic BaseSettings (database URL, CORS origins, logging)
├── database.py                 # SQLAlchemy engine, SessionLocal, declarative Base, get_db dependency
├── middleware/
│   ├── __init__.py
│   └── auth_middleware.py      # Session token validation & role-based dependencies
├── models/
│   ├── __init__.py
│   ├── menu_item.py            # MenuItem ORM model
│   ├── order.py                # Order ORM model
│   ├── order_item.py           # OrderItem ORM model
│   └── session.py              # Session ORM model (auth tokens)
├── schemas/
│   ├── __init__.py
│   ├── auth.py                 # LoginRequest, SessionResponse
│   ├── menu_item.py            # MenuItemCreate, MenuItemUpdate, MenuItemResponse
│   └── order.py                # OrderItemCreate, OrderCreate, OrderItemResponse, OrderResponse
├── routes/
│   ├── __init__.py
│   ├── auth.py                 # /api/v1/auth routes
│   ├── menu.py                 # /api/v1/menu routes (student/public browsing)
│   ├── orders.py               # /api/v1/orders routes (student placement & history)
│   └── admin.py                # /api/v1/admin routes (menu CRUD, inventory, order status, analytics)
├── services/
│   ├── __init__.py
│   ├── analytics_service.py    # AnalyticsService: daily sales, date range sales, popular items
│   ├── auth_service.py         # AuthService: session token generation, validation, expiration, logout
│   ├── inventory_service.py    # InventoryService: stock updates, increments, decrements, thresholds
│   ├── menu_service.py         # MenuService: menu retrieval, search, item CRUD, availability toggle
│   └── order_service.py        # OrderService: order creation, status transitions, validation
└── utils/
    └── __init__.py
```

---

## Database & ORM Layer

### Database Setup (`backend/database.py`)
- **Engine**: SQLite engine created via `create_engine(settings.database_url, connect_args={"check_same_thread": False})`.
- **Session Factory**: `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`.
- **Base**: `Base = declarative_base()`.
- **Session Dependency**: `get_db()` yields a `Session` and guarantees `db.close()` in its `finally` block.
- **Startup**: `init_db()` calls `Base.metadata.create_all(bind=engine)` during FastAPI application lifespan startup.

### Database Models (`backend/models/`)

1. **`MenuItem` (`menu_items`)**:
   - `id`: `Integer`, Primary Key
   - `name`: `String(100)`, unique, non-null, indexed
   - `description`: `String(500)`, non-null
   - `price`: `Numeric(10, 2)`, non-null (positive Decimal)
   - `category`: `String(50)`, non-null, indexed (`meals`, `snacks`, `beverages`, `desserts`)
   - `stock_quantity`: `Integer`, default 0, non-null
   - `stock_threshold`: `Integer`, default 5, non-null
   - `is_available`: `Boolean`, default True, non-null
   - `is_deleted`: `Boolean`, default False, non-null (soft-delete flag)
   - `created_at`, `updated_at`: `DateTime(timezone=True)`

2. **`Order` (`orders`)**:
   - `id`: `Integer`, Primary Key
   - `student_id`: `String(50)`, non-null, indexed
   - `total_price`: `Numeric(10, 2)`, non-null
   - `status`: `String(20)`, default `"pending"`, non-null (`pending`, `preparing`, `ready`, `completed`, `cancelled`)
   - `created_at`, `updated_at`: `DateTime(timezone=True)`
   - `items`: `relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")`

3. **`OrderItem` (`order_items`)**:
   - `id`: `Integer`, Primary Key
   - `order_id`: `Integer`, ForeignKey(`orders.id`), non-null, indexed
   - `menu_item_id`: `Integer`, ForeignKey(`menu_items.id`), non-null, indexed
   - `quantity`: `Integer`, non-null ($\ge 1$)
   - `price_at_order_time`: `Numeric(10, 2)`, non-null (immutable historical price)
   - `order`: `relationship("Order", back_populates="items")`
   - `menu_item`: `relationship("MenuItem")`

4. **`Session` (`sessions`)**:
   - `id`: `Integer`, Primary Key
   - `user_id`: `String(50)`, non-null, indexed
   - `role`: `String(20)`, non-null (`student` or `admin`)
   - `token`: `String(255)`, unique, non-null, indexed (UUIDv4)
   - `created_at`: `DateTime(timezone=True)`
   - `expires_at`: `DateTime(timezone=True)`, non-null (default 24h expiration)

---

## Authentication & Authorization (`backend/middleware/auth_middleware.py`)

Authentication is entirely session-based via tokens passed in the HTTP `Authorization` header:

- **Format**: `Authorization: Bearer <uuid4-token>`
- **Dependencies**:
  - `extract_token`: Extracts and validates the `Bearer <token>` format. Raises `401` on format issues.
  - `get_current_session`: Validates token existence and expiry against `sessions` table.
  - `require_auth`: Ensures user is logged in (student or admin).
  - `require_admin`: Ensures `session.role == 'admin'`, raising `403` otherwise.
  - `require_roles(allowed_roles)`: Parameterized role checker dependency.

---

## Actual API Routes and Endpoints

### 1. System Endpoints (`backend/main.py`)
- `GET /health`: Returns service health status and API version.
- `GET /`: Welcome message and documentation links.

### 2. Authentication Endpoints (`backend/routes/auth.py`, prefix: `/api/v1/auth`)
- `POST /login`: Accepts `LoginRequest(user_id, role)`. Creates session record and returns `SessionResponse` with UUID token.
- `POST /logout`: Invalidate current token session. Requires `extract_token`.

### 3. Student Menu Endpoints (`backend/routes/menu.py`, prefix: `/api/v1/menu`)
- `GET /items`: Returns all available, non-deleted menu items. Query params: `search` (name/desc case-insensitive filter), `category`. Requires `require_auth`.
- `GET /items/{item_id}`: Returns details for an active, available menu item. Returns `404` if not found or unavailable. Requires `require_auth`.

### 4. Student Order Endpoints (`backend/routes/orders.py`, prefix: `/api/v1/orders`)
- `POST /`: Creates a new order. Validates items, availability, stock, and total price. Decrements inventory atomically. **Student only** (admins receive `403 STUDENT_ONLY`). Requires `require_auth`.
- `GET /history`: Returns orders for the authenticated student. Optional query param: `status`. **Student only**. Requires `require_auth`.
- `GET /{order_id}`: Returns details of an order. Students can only access their own order (`403 ACCESS_DENIED` otherwise); admins can view any order. Requires `require_auth`.

### 5. Admin Endpoints (`backend/routes/admin.py`, prefix: `/api/v1/admin`)
All admin endpoints require `Depends(require_admin)`:

- **Menu Management**:
  - `POST /menu/items`: Create new menu item (`MenuItemCreate`). Validates name uniqueness.
  - `PUT /menu/items/{item_id}`: Update menu item fields (`MenuItemUpdate`).
  - `PATCH /menu/items/{item_id}/availability`: Toggle `is_available` boolean.
  - `DELETE /menu/items/{item_id}`: Soft-delete item (`is_deleted = True`).
- **Inventory Management**:
  - `GET /inventory`: Get all menu items with stock levels (including soft-deleted for historical records).
  - `PUT /inventory/{item_id}`: Set explicit stock quantity (must be $\ge 0$).
  - `GET /inventory/low-stock`: Get items where `stock_quantity <= stock_threshold`.
  - `PUT /inventory/{item_id}/threshold`: Update low-stock threshold (must be $\ge 0$).
- **Order Management**:
  - `GET /orders`: View all canteen orders across all students. Optional query param: `status`.
  - `PATCH /orders/{order_id}/status`: Update order status according to `OrderService.VALID_TRANSITIONS`.
- **Analytics**:
  - `GET /analytics/sales/daily`: Get daily total sales revenue, order count, and category breakdown. Query param: `target_date`.
  - `GET /analytics/sales/range`: Get sales metrics over a date range. Query params: `start_date`, `end_date`.
  - `GET /analytics/popular-items`: Get top most frequently ordered items. Query param: `limit` (default 5).

---

## Error Handling & Response Standards

When endpoints fail, they return uniform JSON structures:
```json
{
  "detail": {
    "error": {
      "code": "ERROR_CODE_STRING",
      "message": "Human-readable explanation of error"
    }
  }
}
```

Common error codes in the system:
- `401 Unauthorized`: `UNAUTHORIZED`, `INVALID_AUTH_FORMAT`, `INVALID_SESSION`
- `403 Forbidden`: `FORBIDDEN`, `ADMIN_ACCESS_REQUIRED`, `STUDENT_ONLY`, `ACCESS_DENIED`
- `404 Not Found`: `ITEM_NOT_FOUND`, `ITEM_NOT_AVAILABLE`, `ORDER_NOT_FOUND`, `SESSION_NOT_FOUND`
- `400 Bad Request`: `LOGIN_FAILED`, `MENU_ITEM_VALIDATION_ERROR`, `ORDER_VALIDATION_ERROR`

---

## Architectural Constraints for Development

1. **Thin Routes, Thick Services**: Route functions must strictly validate HTTP inputs/dependencies and delegate execution to `Service` methods. Never place direct database mutations or business calculations inside routes.
2. **Atomic Transactions**: In multi-step operations (like creating an order and decrementing stock), use `db.flush()` and wrap inside `try ... except: db.rollback()` blocks to prevent orphan records or partial stock decrements.
3. **No Framework Invention**: Do not add unnecessary libraries, JWT tokens, Celery workers, Redis, or Docker containers. The application is designed to be lightweight, local-first, and self-contained.
