# Coding Conventions

## Python/FastAPI Conventions

### Style Guide
- Follow **PEP 8** style guide
- Use **type hints** for all function parameters and return values
- Maximum line length: **88 characters** (Black formatter standard)
- Use **docstrings** for all public functions and classes

### Naming Conventions
```python
# Variables and functions: snake_case
menu_item = get_menu_item(item_id)
student_order_count = calculate_order_count()

# Classes: PascalCase
class MenuService:
class OrderItem:

# Constants: UPPER_SNAKE_CASE
MAX_ORDER_QUANTITY = 100
DEFAULT_SESSION_TIMEOUT = 3600

# Private methods/variables: prefix with underscore
def _internal_helper():
self._cached_data = None
```

### Type Hints
```python
from typing import List, Optional, Dict, Any
from decimal import Decimal

def get_menu_items(category: Optional[str] = None) -> List[MenuItem]:
    pass

def calculate_total(items: List[OrderItem]) -> Decimal:
    pass

async def create_order(
    student_id: str,
    items: List[OrderItemCreate]
) -> Order:
    pass
```

### Async/Await
```python
# Use async for I/O operations
async def get_order(order_id: int) -> Order:
    return await db.get(Order, order_id)

# Regular functions for CPU-bound operations
def calculate_popularity_score(orders: List[Order]) -> float:
    return sum(order.total for order in orders) / len(orders)
```

### Error Handling
```python
# Use specific exceptions
from fastapi import HTTPException

# Bad
raise Exception("Not found")

# Good
raise HTTPException(status_code=404, detail="Order not found")

# Service layer - raise custom exceptions
class InsufficientStockError(Exception):
    pass

# Route layer - convert to HTTP exceptions
try:
    order = order_service.create_order(data)
except InsufficientStockError as e:
    raise HTTPException(status_code=400, detail=str(e))
```

### FastAPI Route Patterns
```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter(prefix="/api/v1/menu", tags=["menu"])

@router.get("/items", response_model=List[MenuItemResponse])
async def get_menu_items(
    category: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Get available menu items with optional filtering.
    
    - **category**: Filter by food category
    - **search**: Search in name and description
    """
    return menu_service.get_available_items(category, search)
```

### Database Operations
```python
# Always use SQLAlchemy ORM
from sqlalchemy.orm import Session

# Bad - raw SQL
db.execute("SELECT * FROM menu_items WHERE id = ?", (item_id,))

# Good - ORM
db.query(MenuItem).filter(MenuItem.id == item_id).first()

# Use relationships
order = db.query(Order).filter(Order.id == order_id).first()
items = order.items  # Automatic join via relationship

# Use transactions for multi-step operations
from sqlalchemy.exc import SQLAlchemyError

try:
    # Multiple operations
    order = Order(...)
    db.add(order)
    
    for item in order_items:
        menu_item = db.query(MenuItem).get(item.id)
        menu_item.stock_quantity -= item.quantity
    
    db.commit()
except SQLAlchemyError:
    db.rollback()
    raise
```

## JavaScript/Frontend Conventions

### Style Guide
- Use **ES6+ syntax** (const, let, arrow functions, classes)
- Use **camelCase** for variables and functions
- Use **PascalCase** for classes
- Use **UPPER_SNAKE_CASE** for constants
- Maximum line length: **100 characters**

### Naming Conventions
```javascript
// Variables and functions: camelCase
const menuItems = fetchMenuItems();
const totalPrice = calculateTotal(cartItems);

// Classes: PascalCase
class Cart {
class ApiClient {

// Constants: UPPER_SNAKE_CASE
const MAX_CART_ITEMS = 50;
const API_BASE_URL = 'http://localhost:8000';

// Private properties: prefix with underscore
class Cart {
  constructor() {
    this._items = [];
  }
}
```

### Module Pattern
```javascript
// Use ES6 modules
// cart.js
export class Cart {
  constructor() {
    this.items = [];
  }
  
  addItem(item) {
    // implementation
  }
}

export function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

// main.js
import { Cart, calculateTotal } from './cart.js';
```

### Async/Await for API Calls
```javascript
// Use async/await, not callbacks or raw promises
async function fetchMenuItems() {
  try {
    const response = await fetch('/api/v1/menu/items');
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch menu items:', error);
    throw error;
  }
}

// Call with await
const items = await fetchMenuItems();
```

### Error Handling
```javascript
// Handle errors gracefully
async function placeOrder(cartItems) {
  try {
    const response = await api.post('/orders', { items: cartItems });
    return response;
  } catch (error) {
    if (error.status === 400) {
      displayError('Invalid order. Please check your cart.');
    } else if (error.status === 401) {
      redirectToLogin();
    } else {
      displayError('Failed to place order. Please try again.');
    }
    throw error;
  }
}
```

### DOM Manipulation
```javascript
// Use modern DOM APIs
// Bad - innerHTML for complex structures
container.innerHTML = '<div>...</div>';

// Good - createElement and append
function renderMenuItem(item) {
  const card = document.createElement('div');
  card.className = 'menu-item-card';
  
  const name = document.createElement('h3');
  name.textContent = item.name;
  card.appendChild(name);
  
  // Add more elements...
  
  return card;
}

// Use dataset for data attributes
card.dataset.itemId = item.id;
const itemId = card.dataset.itemId;

// Use event delegation
document.getElementById('menu').addEventListener('click', (e) => {
  if (e.target.classList.contains('add-to-cart')) {
    const itemId = e.target.closest('.menu-item-card').dataset.itemId;
    addToCart(itemId);
  }
});
```

### Local Storage
```javascript
// Consistent localStorage usage
const STORAGE_KEYS = {
  CART: 'canteen_cart',
  SESSION: 'canteen_session'
};

function saveCart(cart) {
  localStorage.setItem(STORAGE_KEYS.CART, JSON.stringify(cart));
}

function loadCart() {
  const data = localStorage.getItem(STORAGE_KEYS.CART);
  return data ? JSON.parse(data) : { items: [] };
}
```

## HTML Conventions

### Semantic HTML
```html
<!-- Use semantic elements -->
<header>
  <nav>
    <ul>
      <li><a href="#menu">Menu</a></li>
    </ul>
  </nav>
</header>

<main>
  <section id="menu">
    <h2>Today's Menu</h2>
    <article class="menu-item">
      <h3>Burger</h3>
      <p>Delicious beef burger</p>
    </article>
  </section>
</main>

<footer>
  <p>&copy; 2026 Kiro University</p>
</footer>
```

### Accessibility
```html
<!-- Use proper labels and ARIA attributes -->
<form>
  <label for="search-input">Search menu items</label>
  <input 
    id="search-input" 
    type="text" 
    placeholder="Search..."
    aria-label="Search menu items"
  >
  
  <button type="submit" aria-label="Search">
    <span aria-hidden="true">🔍</span>
  </button>
</form>

<!-- Use alt text for images -->
<img src="burger.jpg" alt="Beef burger with lettuce and tomato">

<!-- Use semantic buttons -->
<button type="button" onclick="addToCart()">Add to Cart</button>
<!-- Not: <div onclick="addToCart()">Add to Cart</div> -->
```

### Data Attributes
```html
<!-- Use data attributes for JavaScript hooks -->
<div class="menu-item-card" data-item-id="123" data-category="meals">
  <h3>Burger</h3>
  <button class="add-to-cart" data-price="9.99">Add to Cart</button>
</div>
```

## CSS Conventions

### Organization
```css
/* Group styles by component */

/* 1. Reset/Base styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 2. Typography */
body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 16px;
  line-height: 1.6;
}

/* 3. Layout */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

/* 4. Components */
.menu-item-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
}

/* 5. Utilities */
.text-center {
  text-align: center;
}

.hidden {
  display: none;
}
```

### Naming (BEM-inspired)
```css
/* Block__Element--Modifier pattern */
.menu-item {
  /* Block */
}

.menu-item__title {
  /* Element */
}

.menu-item__price {
  /* Element */
}

.menu-item--featured {
  /* Modifier */
}

.menu-item__button--disabled {
  /* Element with Modifier */
}
```

### Responsive Design
```css
/* Mobile-first approach */
.menu-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

/* Tablet */
@media (min-width: 768px) {
  .menu-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .menu-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### CSS Custom Properties
```css
:root {
  /* Colors */
  --primary-color: #2563eb;
  --secondary-color: #64748b;
  --success-color: #10b981;
  --error-color: #ef4444;
  --warning-color: #f59e0b;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Typography */
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.25rem;
  --font-size-xl: 1.5rem;
}

.button-primary {
  background-color: var(--primary-color);
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--font-size-base);
}
```

## General Conventions

### File Naming
- Python files: `snake_case.py`
- JavaScript files: `camelCase.js`
- CSS files: `kebab-case.css`
- HTML files: `kebab-case.html`

### Comments
```python
# Python - Use docstrings for functions/classes
def calculate_total(items: List[OrderItem]) -> Decimal:
    """
    Calculate the total price of order items.
    
    Args:
        items: List of order items with quantity and price
        
    Returns:
        Total price as Decimal
        
    Raises:
        ValueError: If items list is empty
    """
    pass

# Use inline comments sparingly - code should be self-documenting
# Only comment WHY, not WHAT
price = item.price * 0.9  # Apply 10% student discount
```

```javascript
// JavaScript - Use JSDoc for functions
/**
 * Calculate the total price of cart items
 * @param {Array} items - Cart items with quantity and price
 * @returns {number} Total price
 */
function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

// Use inline comments sparingly
const total = calculateSubtotal() * 1.1;  // Add 10% service charge
```

### Git Commit Messages
```
# Format: <type>: <subject>

feat: Add menu item filtering by category
fix: Correct cart total calculation
docs: Update API documentation for orders endpoint
test: Add property tests for inventory service
refactor: Extract order validation logic to service
style: Format code with Black formatter
```

### Code Review Checklist
- [ ] Follows naming conventions
- [ ] Includes type hints (Python) or JSDoc (JavaScript)
- [ ] Has appropriate error handling
- [ ] No hardcoded values (use config or constants)
- [ ] Includes tests for new functionality
- [ ] No console.log or print statements (use logging)
- [ ] Accessible HTML (labels, ARIA attributes)
- [ ] Responsive CSS (mobile-first)
- [ ] No raw SQL queries (use ORM)
