# Testing Guidelines

## Testing Strategy

### Test Pyramid

```
        /\
       /  \      E2E Tests (Few)
      /____\     - Full user workflows
     /      \    - Browser automation
    /        \   
   /__________\  Integration Tests (Some)
  /            \ - API endpoints
 /              \- Component interactions
/________________\ Unit Tests + Property Tests (Many)
                   - Business logic
                   - Calculations
                   - Validation
```

### Test Types

1. **Property-Based Tests**: Core business logic with randomized inputs (100+ iterations)
2. **Unit Tests**: Specific examples, edge cases, error conditions
3. **Integration Tests**: API endpoints, database operations, service interactions
4. **End-to-End Tests**: Complete user workflows

## Property-Based Testing

### When to Use PBT

**Use property-based tests for:**
- Pure functions with clear input/output behavior
- Calculations (totals, revenue, popularity scores)
- Filtering and sorting operations
- Validation logic
- Data transformations
- Inverse operations (add then remove = original state)

**Don't use property-based tests for:**
- UI rendering specifics
- Database schema validation
- External API integrations
- Configuration loading
- Simple CRUD operations

### Python Property Tests (Hypothesis)

```python
from hypothesis import given, strategies as st
import pytest

# Feature: smart-canteen-manager, Property 22: Cart Total Calculation
@given(
    cart_items=st.lists(
        st.fixed_dictionaries({
            'id': st.integers(min_value=1),
            'price': st.decimals(
                min_value=0.01,
                max_value=999.99,
                places=2
            ),
            'quantity': st.integers(min_value=1, max_value=100)
        }),
        min_size=1,
        max_size=20
    )
)
def test_cart_total_equals_sum_of_items(cart_items):
    """
    Property: Cart total equals sum of (price * quantity) for all items
    Validates: Requirements 3.6
    """
    cart = Cart(cart_items)
    
    expected_total = sum(
        item['price'] * item['quantity']
        for item in cart_items
    )
    
    assert cart.calculate_total() == expected_total


# Feature: smart-canteen-manager, Property 31: Price Validation
@given(
    price=st.one_of(
        st.decimals(min_value=0.01, max_value=9999.99, places=2),  # Valid
        st.decimals(max_value=0.00),  # Invalid: <= 0
        st.decimals(min_value=0.01, places=3)  # Invalid: > 2 decimals
    )
)
def test_price_validation_property(price):
    """
    Property: Valid prices are positive with max 2 decimal places
    Validates: Requirements 7.4, 17.5
    """
    result = validate_price(price)
    
    # Valid if >= 0.01 and max 2 decimal places
    is_valid = price >= 0.01 and abs(price.as_tuple().exponent) <= 2
    
    assert result.is_valid == is_valid


# Feature: smart-canteen-manager, Property 39: Stock Increment/Decrement Inverse
@given(
    initial_stock=st.integers(min_value=10, max_value=1000),
    amount=st.integers(min_value=1, max_value=100)
)
def test_stock_operations_are_inverse(initial_stock, amount):
    """
    Property: Increment then decrement returns original stock
    Validates: Requirements 9.5
    """
    # Assume we have a menu item with initial stock
    item = MenuItem(stock_quantity=initial_stock)
    
    # Increment
    inventory_service.increment_stock(item.id, amount)
    assert item.stock_quantity == initial_stock + amount
    
    # Decrement
    inventory_service.decrement_stock(item.id, amount)
    assert item.stock_quantity == initial_stock
```

### JavaScript Property Tests (fast-check)

```javascript
const fc = require('fast-check');

// Feature: smart-canteen-manager, Property 22: Cart Total Calculation
test('cart total equals sum of item prices times quantities', () => {
  fc.assert(
    fc.property(
      fc.array(
        fc.record({
          id: fc.integer({ min: 1 }),
          name: fc.string(),
          price: fc.float({ min: 0.01, max: 999.99 }),
          quantity: fc.integer({ min: 1, max: 100 })
        }),
        { minLength: 1, maxLength: 20 }
      ),
      (cartItems) => {
        const cart = new Cart(cartItems);
        const expectedTotal = cartItems.reduce(
          (sum, item) => sum + (item.price * item.quantity),
          0
        );
        
        // Use toBeCloseTo for floating point comparison
        expect(cart.calculateTotal()).toBeCloseTo(expectedTotal, 2);
      }
    ),
    { numRuns: 100 }  // MUST run at least 100 iterations
  );
});


// Feature: smart-canteen-manager, Property 10: Search Filtering Correctness
test('search returns only items matching query', () => {
  fc.assert(
    fc.property(
      fc.array(
        fc.record({
          id: fc.integer({ min: 1 }),
          name: fc.string({ minLength: 1, maxLength: 50 }),
          description: fc.string({ maxLength: 200 })
        }),
        { minLength: 5, maxLength: 50 }
      ),
      fc.string({ minLength: 1, maxLength: 20 }),
      (menuItems, query) => {
        const menu = new Menu(menuItems);
        const results = menu.search(query);
        
        // All results must contain query (case-insensitive)
        const lowerQuery = query.toLowerCase();
        results.forEach(item => {
          const matchesName = item.name.toLowerCase().includes(lowerQuery);
          const matchesDesc = item.description.toLowerCase().includes(lowerQuery);
          expect(matchesName || matchesDesc).toBe(true);
        });
      }
    ),
    { numRuns: 100 }
  );
});
```

### Property Test Configuration

**Mandatory Settings:**
- Minimum 100 iterations per property test
- Include property number and name in test description
- Add comment referencing design property
- Tag with validated requirements

```python
# Test configuration
pytest.ini:
[pytest]
addopts = --hypothesis-show-statistics
```

## Unit Testing

### Python Unit Tests (pytest)

```python
import pytest
from decimal import Decimal

def test_empty_menu_returns_empty_list():
    """Example: Empty menu returns empty list"""
    service = MenuService(db)
    result = service.get_available_menu_items()
    assert result == []


def test_order_with_unavailable_item_fails():
    """Example: Order with unavailable item is rejected"""
    # Setup
    item = MenuItem(name="Burger", price=9.99, is_available=False)
    db.add(item)
    db.commit()
    
    # Attempt order
    order_data = OrderCreate(items=[
        OrderItemCreate(menu_item_id=item.id, quantity=1)
    ])
    
    with pytest.raises(ValidationError, match="unavailable"):
        order_service.create_order("S001", order_data)


def test_insufficient_stock_rejects_order():
    """Example: Order with insufficient stock is rejected"""
    # Setup
    item = MenuItem(
        name="Burger",
        price=9.99,
        stock_quantity=2,
        is_available=True
    )
    db.add(item)
    db.commit()
    
    # Attempt order for 5 items when only 2 in stock
    order_data = OrderCreate(items=[
        OrderItemCreate(menu_item_id=item.id, quantity=5)
    ])
    
    with pytest.raises(InsufficientStockError):
        order_service.create_order("S001", order_data)


def test_order_creation_decrements_stock():
    """Example: Creating order decrements stock"""
    # Setup
    initial_stock = 10
    order_quantity = 3
    item = MenuItem(
        name="Burger",
        price=9.99,
        stock_quantity=initial_stock,
        is_available=True
    )
    db.add(item)
    db.commit()
    
    # Create order
    order_data = OrderCreate(items=[
        OrderItemCreate(menu_item_id=item.id, quantity=order_quantity)
    ])
    order = order_service.create_order("S001", order_data)
    
    # Verify stock decremented
    db.refresh(item)
    assert item.stock_quantity == initial_stock - order_quantity


@pytest.fixture
def sample_menu_items():
    """Fixture for test data"""
    return [
        MenuItem(name="Burger", price=Decimal("9.99"), category="Meals"),
        MenuItem(name="Pizza", price=Decimal("12.99"), category="Meals"),
        MenuItem(name="Soda", price=Decimal("2.99"), category="Beverages")
    ]
```

### JavaScript Unit Tests (Jest)

```javascript
describe('Cart', () => {
  test('empty cart has zero total', () => {
    const cart = new Cart();
    expect(cart.getTotal()).toBe(0);
    expect(cart.isEmpty()).toBe(true);
  });
  
  test('adding item increases count', () => {
    const cart = new Cart();
    const item = { id: 1, name: 'Burger', price: 9.99 };
    
    cart.addItem(item);
    
    expect(cart.getItemCount()).toBe(1);
    expect(cart.getItems()).toHaveLength(1);
  });
  
  test('removing item decreases count', () => {
    const cart = new Cart();
    cart.addItem({ id: 1, name: 'Burger', price: 9.99 });
    cart.addItem({ id: 2, name: 'Pizza', price: 12.99 });
    
    cart.removeItem(1);
    
    expect(cart.getItemCount()).toBe(1);
    expect(cart.getItems()[0].id).toBe(2);
  });
  
  test('cart persists to localStorage', () => {
    const cart = new Cart();
    cart.addItem({ id: 1, name: 'Burger', price: 9.99 });
    
    cart.save();
    
    const loaded = Cart.load();
    expect(loaded.getItems()).toEqual(cart.getItems());
  });
});


describe('Menu Filtering', () => {
  let menu;
  
  beforeEach(() => {
    menu = new Menu([
      { id: 1, name: 'Burger', category: 'Meals' },
      { id: 2, name: 'Pizza', category: 'Meals' },
      { id: 3, name: 'Soda', category: 'Beverages' }
    ]);
  });
  
  test('filters by category', () => {
    const filtered = menu.filterByCategory('Meals');
    expect(filtered).toHaveLength(2);
    filtered.forEach(item => {
      expect(item.category).toBe('Meals');
    });
  });
  
  test('search returns matching items', () => {
    const results = menu.search('burg');
    expect(results).toHaveLength(1);
    expect(results[0].name).toBe('Burger');
  });
  
  test('search is case-insensitive', () => {
    const results = menu.search('PIZZA');
    expect(results).toHaveLength(1);
    expect(results[0].name).toBe('Pizza');
  });
});
```

## Integration Testing

### Backend Integration Tests

```python
from fastapi.testclient import TestClient

def test_create_order_endpoint_integration(client, auth_header):
    """Integration: POST /orders creates order and decrements stock"""
    # Setup: Create menu item
    response = client.post(
        "/api/v1/admin/menu/items",
        json={
            "name": "Burger",
            "description": "Beef burger",
            "price": 9.99,
            "category": "Meals",
            "stock_quantity": 10
        },
        headers=admin_auth_header
    )
    item_id = response.json()["id"]
    
    # Place order
    response = client.post(
        "/api/v1/orders",
        json={
            "items": [
                {"menu_item_id": item_id, "quantity": 3}
            ]
        },
        headers=auth_header
    )
    
    # Assert order created
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["total_price"] == 29.97
    
    # Verify stock decremented
    response = client.get(
        f"/api/v1/admin/inventory",
        headers=admin_auth_header
    )
    inventory = response.json()
    item = next(i for i in inventory if i["id"] == item_id)
    assert item["stock_quantity"] == 7


def test_unauthorized_access_to_admin_endpoint(client):
    """Integration: Admin endpoints require admin role"""
    # Student token
    student_header = get_auth_header(user_id="S001", role="student")
    
    response = client.get(
        "/api/v1/admin/orders",
        headers=student_header
    )
    
    assert response.status_code == 403


def test_authentication_required(client):
    """Integration: Protected endpoints require authentication"""
    response = client.get("/api/v1/menu/items")
    assert response.status_code == 401


@pytest.fixture
def client():
    """Test client with database setup"""
    # Use in-memory database for tests
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    app.dependency_overrides[get_db] = lambda: TestingSessionLocal()
    
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_header(client):
    """Authenticated student header"""
    response = client.post(
        "/api/v1/auth/login",
        json={"user_id": "S001", "role": "student"}
    )
    token = response.json()["token"]
    return {"Authorization": f"Bearer {token}"}
```

### Frontend Integration Tests

```javascript
describe('Menu API Integration', () => {
  let api;
  
  beforeEach(() => {
    api = new ApiClient('http://localhost:8000');
    global.fetch = jest.fn();
  });
  
  test('fetches menu items', async () => {
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => [
        { id: 1, name: 'Burger', price: 9.99 },
        { id: 2, name: 'Pizza', price: 12.99 }
      ]
    });
    
    const items = await api.getMenuItems();
    
    expect(items).toHaveLength(2);
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/menu/items',
      expect.objectContaining({
        method: 'GET'
      })
    );
  });
  
  test('handles API errors', async () => {
    global.fetch.mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({ error: { message: 'Server error' } })
    });
    
    await expect(api.getMenuItems()).rejects.toThrow('Server error');
  });
  
  test('includes auth token in requests', async () => {
    AuthService.storeSession('test-token', 'S001', 'student');
    
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => []
    });
    
    await api.getMenuItems();
    
    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': 'Bearer test-token'
        })
      })
    );
  });
});
```

## Test Organization

### Directory Structure

```
tests/
├── properties/              # Property-based tests
│   ├── test_cart_properties.py
│   ├── test_menu_properties.py
│   ├── test_order_properties.py
│   └── test_validation_properties.py
├── unit/                    # Unit tests
│   ├── test_menu_service.py
│   ├── test_order_service.py
│   ├── test_inventory_service.py
│   └── test_analytics_service.py
├── integration/             # Integration tests
│   ├── test_api_endpoints.py
│   ├── test_database.py
│   └── test_auth_flow.py
└── e2e/                     # End-to-end tests
    ├── test_student_workflow.py
    └── test_admin_workflow.py
```

### Test Naming Conventions

```python
# Property tests: test_<property_name>
def test_cart_total_equals_sum_of_items():
    pass

# Unit tests: test_<function>_<scenario>
def test_create_order_with_valid_items():
    pass

def test_create_order_with_insufficient_stock_fails():
    pass

# Integration tests: test_<endpoint>_<scenario>
def test_post_orders_creates_order_and_decrements_stock():
    pass
```

## Test Coverage

### Coverage Goals
- Backend: Minimum 80% code coverage
- Frontend: Minimum 75% code coverage
- All 56 correctness properties tested
- All API endpoints integration tested
- Critical user workflows E2E tested

### Running Tests with Coverage

```bash
# Python tests with coverage
pytest tests/ -v --cov=backend --cov-report=html --cov-report=term

# JavaScript tests with coverage
npm test -- --coverage --coverageReporters=html --coverageReporters=text

# Property tests only
pytest tests/properties/ -v

# Integration tests only
pytest tests/integration/ -v

# Specific test file
pytest tests/unit/test_order_service.py -v
```

## Mocking and Fixtures

### Mocking External Services

```python
@pytest.fixture
def mock_ai_service(monkeypatch):
    """Mock AI service for testing"""
    def mock_response(question, context):
        if "menu" in question.lower():
            return "Today's menu includes burgers and pizza."
        return "I'm here to help with canteen questions."
    
    monkeypatch.setattr(
        'services.ai_service.AIService.get_ai_response',
        mock_response
    )
    return mock_response
```

### Database Fixtures

```python
@pytest.fixture
def db_session():
    """In-memory database session"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()


@pytest.fixture
def sample_menu_items(db_session):
    """Sample menu items for testing"""
    items = [
        MenuItem(name="Burger", price=9.99, stock_quantity=10),
        MenuItem(name="Pizza", price=12.99, stock_quantity=5)
    ]
    for item in items:
        db_session.add(item)
    db_session.commit()
    return items
```

## Testing Best Practices

### DO
- ✅ Write tests before or alongside implementation
- ✅ Test one thing per test
- ✅ Use descriptive test names
- ✅ Follow AAA pattern (Arrange, Act, Assert)
- ✅ Use fixtures for reusable test data
- ✅ Mock external dependencies
- ✅ Run tests frequently during development
- ✅ Keep tests fast (unit tests under 100ms)
- ✅ Test edge cases and error conditions
- ✅ Use property tests for business logic

### DON'T
- ❌ Skip tests to save time
- ❌ Test implementation details
- ❌ Write tests that depend on each other
- ❌ Use real external services in tests
- ❌ Hardcode test data that should be randomized
- ❌ Write tests without assertions
- ❌ Ignore failing tests
- ❌ Make tests too complex
- ❌ Test framework code or libraries

## CI/CD Integration

### Test Pipeline

```yaml
# Example GitHub Actions workflow
name: Test Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run property tests
        run: pytest tests/properties/ -v
      
      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=backend
      
      - name: Run integration tests
        run: pytest tests/integration/ -v
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Property Test Tag Format

All property-based tests MUST include this comment format:

```python
# Feature: smart-canteen-manager, Property N: Property Title
```

Where:
- **Feature**: `smart-canteen-manager`
- **Property N**: Property number from design document (1-56)
- **Property Title**: Property name from design document

Example:
```python
# Feature: smart-canteen-manager, Property 22: Cart Total Calculation
@given(cart_items=...)
def test_cart_total_calculation(cart_items):
    """
    Property: Cart total equals sum of (price * quantity) for all items
    Validates: Requirements 3.6
    """
    pass
```
