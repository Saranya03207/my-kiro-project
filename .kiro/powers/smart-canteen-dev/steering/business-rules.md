# Business Rules - Smart Canteen Development

## User Roles and Authorization

The system enforces strict role-based access control with two distinct roles:

### Student Role
- **Menu Browsing**: Students can only access items that are available (`is_available == True`) and not deleted (`is_deleted == False`). Unavailable or soft-deleted items return `404 Not Found`.
- **Information Hiding**: Students cannot see internal inventory stock counts or threshold alerts.
- **Cart & Ordering**: Students manage their shopping cart client-side. When submitting an order (`POST /api/v1/orders/`), the backend validates stock and availability.
- **Order Placement**: Only students can place orders (`POST /api/v1/orders/`). Admins attempting to place orders receive `403 Forbidden` (`STUDENT_ONLY`).
- **Order History & Tracking**: Students can only view their own orders (`GET /api/v1/orders/history` and `GET /api/v1/orders/{order_id}`). Attempting to view another student's order returns `403 Forbidden` (`ACCESS_DENIED`).

### Admin Role
- **Menu Management**: Full CRUD permissions on menu items:
  - Create new items with unique names
  - Update name, description, price, category, stock quantity, and threshold
  - Toggle item availability (`is_available`)
  - Soft-delete menu items (`is_deleted = True`) to preserve referential integrity
- **Inventory Oversight**: Admins can inspect complete stock levels for all menu items (including deleted items) via `GET /api/v1/admin/inventory`.
- **Stock Thresholds & Alerts**: Low-stock items are dynamically computed when `stock_quantity <= stock_threshold`. Admins can adjust the threshold per item (default is 5).
- **Order Processing**: Admins can view all orders across all students (`GET /api/v1/admin/orders`) and advance order statuses.
- **Analytics Access**: Access to daily sales totals, date-range revenue trends, and top popular items.
- **Ordering Restriction**: Admins cannot place food orders through the customer ordering endpoints.

---

## Order Lifecycle & State Machine

Order state transitions are strictly governed by `OrderService.VALID_TRANSITIONS`:

```
           ┌───────────┐
           │  PENDING  │
           └─────┬─────┘
                 │
                 ├───► [ CANCELLED ] (Valid)
                 ▼
          ┌─────────────┐
          │  PREPARING  │
          └──────┬──────┘
                 │
                 ├───► [ CANCELLED ] (Valid)
                 ▼
          ┌─────────────┐
          │    READY    │
          └──────┬──────┘
                 │
                 ├───► [ CANCELLED ] (Valid)
                 ▼
          ┌─────────────┐
          │  COMPLETED  │ (Terminal State)
          └─────────────┘
```

### Transition Specifications

| Current Status | Allowed Next Statuses | Transition Rationale |
| :--- | :--- | :--- |
| **`pending`** | `preparing`, `cancelled` | Order received by canteen; staff begins preparation or cancels order |
| **`preparing`** | `ready`, `cancelled` | Food is actively being prepared; completed or cancelled due to kitchen issues |
| **`ready`** | `completed`, `cancelled` | Food is at counter waiting for pickup; customer collects it or order is cancelled |
| **`completed`** | *(none)* | Terminal state; completed orders cannot be transitioned |
| **`cancelled`** | *(none)* | Terminal state; cancelled orders cannot be reopened |

### Invalid Transitions
Any transition not defined in the table above raises a `ValueError("Invalid status transition: <from> → <to>")` and is rejected by the API with HTTP `400 Bad Request`.
- No backward transitions (e.g., `preparing → pending` or `ready → preparing` are rejected).
- Terminal states (`completed`, `cancelled`) cannot be modified.

---

## Data Validation Rules

### Menu Items
1. **Name**:
   - Must be between 1 and 100 characters.
   - Cannot be empty or contain only whitespace.
   - Must be unique across all non-deleted menu items (enforced via database unique constraint and service validation).
2. **Description**:
   - Must be between 1 and 500 characters.
   - Cannot be empty or contain only whitespace.
3. **Price**:
   - Must be a positive `Decimal` between `0.01` and `9999.99`.
   - Maximum of 2 decimal places. Floating-point types are strictly forbidden.
4. **Category**:
   - Must be between 1 and 50 characters (`meals`, `snacks`, `beverages`, `desserts`).
   - Cannot be empty or whitespace only.
5. **Stock Quantity**:
   - Must be an integer $\ge 0$.
6. **Stock Threshold**:
   - Must be an integer $\ge 0$ (defaults to 5).
7. **Soft Delete**:
   - Items are never hard-deleted from the database. Setting `is_deleted = True` hides the item from student views while maintaining referential integrity for past orders and analytics.

### Orders and Order Items
1. **Item Count**:
   - An order must contain at least 1 item (`OrderCreate.items` min length 1).
2. **Item Quantity**:
   - Each ordered item must have a quantity $\ge 1$ (`OrderItemCreate.quantity >= 1`).
3. **Menu Item Existence**:
   - Each `menu_item_id` in an order must refer to an existing, non-deleted `MenuItem`.
4. **Item Availability**:
   - Each ordered item must currently have `is_available == True`.
5. **Stock Availability & Atomic Decrement**:
   - The canteen must have sufficient stock (`menu_item.stock_quantity >= item.quantity`).
   - On order creation, stock is decremented atomically inside the database transaction:
     $$\text{stock}_{\text{new}} = \text{stock}_{\text{current}} - \text{quantity}_{\text{ordered}}$$
   - If stock is insufficient, the transaction rolls back, raises a `ValueError("Insufficient stock")`, and leaves inventory unmodified.
6. **Price Locking**:
   - When an order is placed, the current menu item price is saved into `OrderItem.price_at_order_time`. Subsequent changes to menu item prices do NOT alter past order prices.
7. **Total Price Calculation**:
   - `Order.total_price` is computed deterministically as:
     $$\text{Total Price} = \sum_{i=1}^{n} (\text{price\_at\_order\_time}_i \times \text{quantity}_i)$$

---

## Business Invariants Enforced by Tests

The existing test suite actively verifies and protects the following invariants:

1. **Total Price Invariant**: For any placed order, `order.total_price` equals the exact arithmetic sum of each item's unit price multiplied by its quantity.
2. **Inventory Conservation Invariant**: For any successful order, `remaining_stock == initial_stock - quantity`. Stock can never drop below 0.
3. **Order Status Validity Invariant**: Orders can only transition through `OrderService.VALID_TRANSITIONS`. Invalid transitions are rejected without modifying order state.
4. **Data Isolation Invariant**: Student session tokens can only query or read orders where `order.student_id == session.user_id`.
5. **Foreign Key Integrity Invariant**: OrderItems cannot reference non-existent `orders.id` or `menu_items.id`. SQLite foreign key constraint enforcement is verified in tests.
