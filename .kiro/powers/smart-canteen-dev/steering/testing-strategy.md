# Testing Strategy - Smart Canteen Development

## Testing Architecture

The Smart Canteen test suite is structured into three tiers: isolated unit tests for domain services/schemas, end-to-end integration tests for API routes, and property-based invariant tests using Hypothesis.

```
tests/
├── conftest.py                             # Root test configuration (Python path setup)
├── unit/                                   # Domain services and Pydantic schema unit tests
│   ├── test_analytics_service.py           # Daily sales, revenue metrics, popular items calculation
│   ├── test_auth_schemas.py                # LoginRequest and SessionResponse validation
│   ├── test_auth_service.py                # UUID token generation, session lifecycle, expiration
│   ├── test_inventory_service.py           # Stock get/update/increment/decrement, low-stock filter
│   ├── test_menu_schemas.py                # MenuItemCreate, MenuItemUpdate, price/length validation
│   ├── test_menu_service.py                # Menu search, category filter, availability toggle, soft delete
│   ├── test_order_schemas.py               # OrderCreate, OrderItemCreate, quantity & item count rules
│   └── test_order_service.py               # Order placement, atomic stock checks, status transitions
├── integration/                            # FastAPI TestClient API route integration tests
│   ├── test_admin_routes.py                # Menu CRUD, inventory endpoints, admin order management
│   ├── test_auth_routes.py                 # Login, logout, header token validation, 401 handling
│   ├── test_health_check.py                # /health and root / endpoint checks
│   ├── test_menu_routes.py                 # Student menu browsing, search, and availability checks
│   └── test_orders_routes.py               # Student order creation, history, and status tracking
└── properties/                             # Hypothesis property-based testing (Lesson 4)
    ├── test_foreign_key_constraints.py     # SQLite referential integrity & foreign key enforcement
    ├── test_order_business_properties.py   # Order totals, stock conservation, lifecycle invariants
    └── test_schema_validation_properties.py# Schema input boundary generation & invariant verification
```

---

## Test Execution

Run the complete test suite from the repository root:

```bash
pytest -q --tb=no
```

### Verified Test Suite
The test suite collects **302 tests** across unit, integration, and property-based test suites.
- 286 unit and integration tests covering services, routes, schemas, and authentication.
- 16 property-based tests verifying domain invariants with Hypothesis.

Note on Hypothesis deadlines: In environments with variable database I/O timing, tests that do not explicitly configure `@settings(deadline=None)` may occasionally encounter Hypothesis `DeadlineExceeded` (200ms default deadline) during SQLite in-memory initialization. Explicitly configuring `deadline=None` is recommended for property tests.

Specific test suites can be executed independently:
```bash
# Unit tests
pytest tests/unit/ -q

# Integration tests
pytest tests/integration/ -q

# Property-based tests
pytest tests/properties/ -q
```

---

## Property-Based Testing with Hypothesis

Property-based tests automatically generate hundreds of edge-case inputs to mathematically verify that business invariants hold across arbitrary valid inputs.

### Framework & Configuration
- Uses `hypothesis.given`, `hypothesis.strategies as st`, and `hypothesis.settings`.
- `@settings(max_examples=100, deadline=None)` ensures adequate coverage without flaky timeouts in varied environments.

### Core Invariants Verified by Property Tests

#### 1. Order Total Price Invariant (`tests/properties/test_order_business_properties.py`)
For any order with $n$ arbitrary items ($1 \le n \le 10$), random quantities ($1 \le q_i \le 20$), and prices generated as Decimals ($0.01 \le p_i \le 999.99$ with 2 decimal places):
$$\text{order.total\_price} == \sum_{i=1}^{n} (p_i \times q_i)$$
Subtotals must never drift or lose precision due to floating-point rounding.

#### 2. Stock Conservation & Non-Negative Invariant
When an order is created:
- Each item's stock decreases by the exact ordered quantity:
  $$\text{stock}_{\text{after}} == \text{stock}_{\text{before}} - \text{quantity}$$
- If requested quantity exceeds stock ($\text{quantity} > \text{stock}$), the operation raises `ValueError("Insufficient stock")` and leaves inventory unchanged.
- Stock quantity cannot be set to a negative number.

#### 3. Schema Boundary Invariants (`tests/properties/test_schema_validation_properties.py`)
- **Quantity Validation**: For any integer $Q$, `OrderItemCreate` succeeds if and only if $Q \ge 1$. $Q \le 0$ raises `ValidationError`.
- **Item Count Validation**: An order must contain at least 1 item. Empty lists raise `ValidationError`.
- **Price Precision**: Prices with more than 2 decimal places are rejected.
- **String Sanitization**: Empty strings or strings with only whitespace for names or descriptions raise `ValidationError`.

#### 4. Referential Integrity Invariant (`tests/properties/test_foreign_key_constraints.py`)
- SQLite requires explicit activation of foreign key constraints in tests:
  ```python
  @event.listens_for(engine, "connect")
  def set_sqlite_pragma(dbapi_conn, connection_record):
      cursor = dbapi_conn.cursor()
      cursor.execute("PRAGMA foreign_keys=ON")
      cursor.close()
  ```
- Any attempt to create an `OrderItem` referencing a non-existent `order_id` or `menu_item_id` triggers an `IntegrityError`.

---

## Test Database Fixtures & Isolation

Integration tests use FastAPI `TestClient` with in-memory SQLite databases:

1. **Shared In-Memory URI**: `sqlite:///file::memory:?cache=shared&uri=true` with `connect_args={"check_same_thread": False, "uri": True}`.
2. **Dependency Overrides**:
   ```python
   app.dependency_overrides[get_db] = override_get_db
   ```
3. **Session Teardown**: Databases and connections are properly cleared and closed per fixture to prevent lock contention.

---

## Critical Testing Invariant

> **STRICT REGRESSION RULE**:
> Existing tests must NOT be weakened, deleted, bypassed, or modified merely to make a change pass.
>
> All 302 tests must continue to pass before and after any implementation or refactoring work.
